"""
OpenClaw status publication service.

Manages periodic status updates and state change notifications.

Reference: specs/openclaw_integration.md Section 1 and 6.2
"""

import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID
import httpx
import os
from dotenv import load_dotenv

from chimera_factory.openclaw.models import (
    StatusPublication,
    AgentStatus,
    AgentResources,
    AgentCapability,
    AgentReputation,
)
from chimera_factory.openclaw.service import OpenClawService
from chimera_factory.db import get_agent_by_id
from chimera_factory.utils.logging import setup_logger

load_dotenv()

logger = setup_logger(__name__)


def calculate_availability(resources: AgentResources) -> str:
    """
    Calculate availability status based on resource metrics.
    
    Reference: specs/openclaw_integration.md Section 1.3
    
    Args:
        resources: Agent resource metrics
        
    Returns:
        Availability status: "available", "busy", or "unavailable"
    """
    # High resource usage = busy
    max_tasks = resources.max_concurrent_tasks or 10
    if (resources.cpu_usage_percent > 80 or 
        resources.memory_usage_percent > 80 or
        resources.queue_depth >= max_tasks):
        return "busy"
    
    # Very high resource usage = unavailable
    if (resources.cpu_usage_percent > 95 or
        resources.memory_usage_percent > 95):
        return "unavailable"
    
    # Otherwise available
    return "available"


class OpenClawStatusService:
    """
    Service for managing agent status publication to OpenClaw.
    
    Reference: specs/openclaw_integration.md Section 6.2
    """
    
    def __init__(self, agent_id: UUID, openclaw_service: Optional[OpenClawService] = None):
        """
        Initialize status service.
        
        Args:
            agent_id: Agent identifier
            openclaw_service: OpenClaw service instance (creates new if None)
        """
        self.agent_id = agent_id
        self.openclaw_service = openclaw_service or OpenClawService()
        self.last_full_update: Optional[datetime] = None
        self.status_cache: Dict[str, Any] = {}
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._running = False
    
    async def get_current_status(self) -> AgentStatus:
        """
        Get current agent status (lightweight).
        
        Returns:
            AgentStatus with current state
        """
        # Get agent from database
        agent_data = get_agent_by_id(self.agent_id)
        if not agent_data:
            raise ValueError(f"Agent {self.agent_id} not found")
        
        # Get current resource metrics (simplified - in production, use actual metrics)
        resources = await self._get_resource_metrics()
        availability = calculate_availability(resources)
        
        # Get capabilities (simplified - in production, check actual skill availability)
        capabilities = await self._get_agent_capabilities()
        
        return AgentStatus(
            agent_id=self.agent_id,
            agent_name=agent_data.get("name", "Unknown Agent"),
            status=agent_data.get("status", "idle"),
            availability=availability,
            capabilities=capabilities,
            resources=resources,
            reputation=await self._get_reputation(),
            last_updated=datetime.now()
        )
    
    async def get_full_status(self) -> StatusPublication:
        """
        Get full agent status for publication.
        
        Returns:
            StatusPublication with complete status information
        """
        status = await self.get_current_status()
        
        return StatusPublication(
            agent_id=status.agent_id,
            agent_name=status.agent_name,
            status=status.status,
            availability=status.availability,
            capabilities=status.capabilities,
            resources=status.resources,
            reputation=status.reputation,
            last_updated=status.last_updated,
            network_endpoint=None  # TODO: Get actual MCP endpoint
        )
    
    async def _get_resource_metrics(self) -> AgentResources:
        """
        Get current resource metrics.
        
        In production, this would query actual system metrics.
        For now, returns default values.
        """
        # TODO: Implement actual resource monitoring
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
        except ImportError:
            # Fallback if psutil not available
            cpu_percent = 25.0
            memory_percent = 40.0
        
        return AgentResources(
            cpu_usage_percent=cpu_percent,
            memory_usage_percent=memory_percent,
            queue_depth=0,  # TODO: Get actual queue depth
            max_concurrent_tasks=10,
            available_slots=10
        )
    
    async def _get_agent_capabilities(self) -> List[AgentCapability]:
        """
        Get agent capabilities.
        
        Returns list of available skills.
        """
        # Get available skills from skills directory
        capabilities = []
        
        # Check if skills are available
        skill_ids = ["trend_research", "content_generation", "engagement_management"]
        for skill_id in skill_ids:
            # In production, check actual skill availability
            capabilities.append(AgentCapability(
                skill_id=skill_id,
                skill_name=skill_id.replace("_", " ").title(),
                description=f"{skill_id.replace('_', ' ')} capability",
                status="available"  # TODO: Check actual status
            ))
        
        return capabilities
    
    async def _get_reputation(self) -> Optional[AgentReputation]:
        """
        Get agent reputation metrics.
        
        In production, this would query reputation system.
        """
        # TODO: Implement reputation system
        return AgentReputation(
            score=0.8,  # Default reputation
            total_collaborations=0,
            success_rate=1.0
        )
    
    async def publish_heartbeat(self) -> bool:
        """
        Publish lightweight status update (heartbeat).
        
        Reference: specs/openclaw_integration.md Section 1.4
        
        Returns:
            True if published successfully (or in mock mode)
        """
        try:
            status = await self.get_current_status()
            
            # Publish via OpenClaw service
            # Try MCP Resource publication first, fallback to HTTP API
            if self.openclaw_service.is_network_available():
                # Attempt MCP resource publication
                try:
                    await self._publish_via_mcp_resource(status)
                    logger.debug(f"Heartbeat published via MCP for agent {self.agent_id}")
                    return True
                except Exception as mcp_error:
                    logger.debug(f"MCP publication failed, trying HTTP API: {mcp_error}")
                    # Fallback to HTTP API
                    try:
                        await self._publish_via_http_api(status)
                        logger.debug(f"Heartbeat published via HTTP API for agent {self.agent_id}")
                        return True
                    except Exception as http_error:
                        logger.warning(f"Both MCP and HTTP publication failed: {http_error}")
                        return False
            else:
                logger.debug(f"OpenClaw network not available, heartbeat skipped for agent {self.agent_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to publish heartbeat: {e}", exc_info=True)
            return False
    
    async def publish_full_status(self) -> bool:
        """
        Publish complete status update.
        
        Reference: specs/openclaw_integration.md Section 1.4
        
        Returns:
            True if published successfully (or in mock mode)
        """
        try:
            status = await self.get_full_status()
            
            # Publish via OpenClaw service
            # Try MCP Resource publication first, fallback to HTTP API
            if self.openclaw_service.is_network_available():
                # Attempt MCP resource publication
                try:
                    await self._publish_via_mcp_resource(status)
                    logger.info(f"Full status published via MCP for agent {self.agent_id}")
                    self.last_full_update = datetime.now()
                    return True
                except Exception as mcp_error:
                    logger.debug(f"MCP publication failed, trying HTTP API: {mcp_error}")
                    # Fallback to HTTP API
                    try:
                        await self._publish_via_http_api(status)
                        logger.info(f"Full status published via HTTP API for agent {self.agent_id}")
                        self.last_full_update = datetime.now()
                        return True
                    except Exception as http_error:
                        logger.warning(f"Both MCP and HTTP publication failed: {http_error}")
                        return False
            else:
                logger.debug(f"OpenClaw network not available, full status skipped for agent {self.agent_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to publish full status: {e}", exc_info=True)
            return False
    
    async def _publish_via_mcp_resource(self, status: AgentStatus) -> None:
        """
        Publish agent status via MCP Resource protocol.
        
        Reference: specs/openclaw_integration.md Section 1.1 (MCP Resource publication)
        
        Args:
            status: Agent status to publish
            
        Raises:
            Exception: If MCP publication fails
        """
        try:
            # MCP Resource URI format: openclaw://agent/{agent_id}/status
            resource_uri = f"openclaw://agent/{self.agent_id}/status"
            
            # Convert status to MCP resource format
            resource_content = {
                "agent_id": str(status.agent_id),
                "agent_name": status.agent_name,
                "status": status.status,
                "availability": status.availability,
                "capabilities": [cap.model_dump() for cap in status.capabilities],
                "resources": status.resources.model_dump(),
                "reputation": status.reputation.model_dump() if status.reputation else None,
                "last_updated": status.last_updated.isoformat(),
                "network_endpoint": str(status.network_endpoint) if status.network_endpoint else None
            }
            
            # Check if MCP client is available
            # In a real implementation, this would use an MCP client library
            # For now, we'll check if we can use MCP via environment variable
            mcp_enabled = os.getenv("OPENCLAW_USE_MCP", "false").lower() == "true"
            
            if mcp_enabled:
                # Attempt to use MCP client if available
                # This would typically use an MCP SDK or client library
                # Example: mcp_client.publish_resource(uri=resource_uri, content=resource_content, ttl=60)
                logger.debug(f"MCP resource publication enabled, would publish to {resource_uri}")
                # In production, this would be:
                # from mcp import MCPClient
                # client = MCPClient()
                # client.publish_resource(uri=resource_uri, content=resource_content, ttl=60)
                raise NotImplementedError("MCP client library not available, falling back to HTTP API")
            else:
                raise NotImplementedError("MCP publication disabled, use HTTP API")
                
        except NotImplementedError:
            # Re-raise to trigger HTTP fallback
            raise
        except Exception as e:
            logger.error(f"MCP resource publication failed: {e}", exc_info=True)
            raise
    
    async def _publish_via_http_api(self, status: AgentStatus) -> None:
        """
        Publish agent status via HTTP API (fallback method).
        
        Reference: specs/openclaw_integration.md Section 1.1 (HTTP API fallback)
        
        Args:
            status: Agent status to publish
            
        Raises:
            Exception: If HTTP publication fails
        """
        try:
            # Use OpenClaw service HTTP API
            publication = StatusPublication(
                agent_id=status.agent_id,
                agent_name=status.agent_name,
                status=status.status,
                availability=status.availability,
                capabilities=status.capabilities,
                resources=status.resources,
                reputation=status.reputation,
                last_updated=status.last_updated,
                network_endpoint=status.network_endpoint
            )
            
            # Publish via OpenClaw service HTTP endpoint
            # The service handles the actual HTTP call
            client = await self.openclaw_service._get_client()
            response = await client.post(
                "/publish",
                json=publication.model_dump()
            )
            response.raise_for_status()
            
            logger.debug(f"Status published via HTTP API for agent {self.agent_id}")
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP API publication failed: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"HTTP API publication error: {e}", exc_info=True)
            raise
    
    async def on_state_change(self, new_state: str) -> bool:
        """
        Handle state change event.
        
        Reference: specs/openclaw_integration.md Section 1.1
        
        Args:
            new_state: New agent state
            
        Returns:
            True if published successfully
        """
        logger.info(f"Agent {self.agent_id} state changed to {new_state}")
        
        # Publish full status on state change
        success = await self.publish_full_status()
        
        if success:
            # Log state change
            logger.info(f"State change logged for agent {self.agent_id}: {new_state}")
        
        return success
    
    async def start_heartbeat(self):
        """
        Start periodic status updates (heartbeat).
        
        Reference: specs/openclaw_integration.md Section 6.2
        
        Heartbeat frequency: Every 30 seconds
        Full update frequency: Every 5 minutes
        """
        if self._running:
            logger.warning("Heartbeat already running")
            return
        
        self._running = True
        last_full_update_time = datetime.now()
        
        logger.info(f"Starting heartbeat for agent {self.agent_id}")
        
        while self._running:
            try:
                # Publish heartbeat every 30 seconds
                await self.publish_heartbeat()
                
                # Publish full status every 5 minutes
                now = datetime.now()
                if (now - last_full_update_time).total_seconds() >= 300:
                    await self.publish_full_status()
                    last_full_update_time = now
                
                # Wait 30 seconds before next heartbeat
                await asyncio.sleep(30)
                
            except asyncio.CancelledError:
                logger.info(f"Heartbeat cancelled for agent {self.agent_id}")
                break
            except Exception as e:
                logger.error(f"Error in heartbeat loop: {e}", exc_info=True)
                # Continue running even on errors
                await asyncio.sleep(30)
    
    def stop_heartbeat(self):
        """Stop periodic status updates."""
        self._running = False
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        logger.info(f"Heartbeat stopped for agent {self.agent_id}")
    
    async def close(self):
        """Close service and cleanup."""
        self.stop_heartbeat()
        if self.openclaw_service:
            await self.openclaw_service.close()
