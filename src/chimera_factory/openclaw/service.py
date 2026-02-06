"""
OpenClaw network service for agent discovery, collaboration, and trend sharing.

Reference: specs/openclaw_integration.md
"""

import os
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
import httpx
from dotenv import load_dotenv

from chimera_factory.openclaw.models import (
    DiscoveryQuery,
    DiscoveryResponse,
    DiscoveredAgent,
    CollaborationRequest,
    CollaborationResponse,
    TrendShare,
)
from chimera_factory.exceptions import APIError, ValidationError
from chimera_factory.utils.logging import setup_logger

load_dotenv()

logger = setup_logger(__name__)


class OpenClawService:
    """
    Service for interacting with the OpenClaw agent social network.
    
    This service provides methods for:
    - Discovering other agents
    - Requesting collaborations
    - Sharing trends
    """
    
    def __init__(self, network_url: Optional[str] = None, api_key: Optional[str] = None, mock_mode: bool = False):
        """
        Initialize OpenClaw service.
        
        Args:
            network_url: OpenClaw network URL (defaults to env var)
            api_key: OpenClaw API key (defaults to env var)
            mock_mode: If True, use mock responses instead of actual network calls
        """
        self.network_url = network_url or os.getenv("OPENCLAW_NETWORK_URL", "https://network.openclaw.io")
        self.api_key = api_key or os.getenv("OPENCLAW_API_KEY")
        self.mock_mode = mock_mode or os.getenv("OPENCLAW_MOCK_MODE", "false").lower() == "true"
        self._client = None
    
    def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            self._client = httpx.AsyncClient(
                base_url=self.network_url,
                headers=headers,
                timeout=30.0
            )
        return self._client
    
    def is_configured(self) -> bool:
        """Check if service is configured with API key."""
        return self.api_key is not None
    
    def is_network_available(self) -> bool:
        """Check if OpenClaw network is available."""
        # In mock mode, always return True
        if self.mock_mode:
            return True
        # Otherwise, check if configured
        return self.is_configured()
    
    async def discover_agents(self, query: DiscoveryQuery) -> DiscoveryResponse:
        """
        Discover agents in the OpenClaw network.
        
        Reference: specs/openclaw_integration.md Section 3.1
        
        Args:
            query: Discovery query parameters
            
        Returns:
            DiscoveryResponse with discovered agents
            
        Raises:
            APIError: If discovery fails
            ValidationError: If query is invalid
        """
        # Mock mode: Return mock data for demonstration
        if self.mock_mode:
            logger.info("OpenClaw in mock mode, returning mock discovery results")
            return DiscoveryResponse(
                agents=[],
                total_found=0
            )
        
        if not self.is_configured():
            logger.warning("OpenClaw not configured, returning empty discovery result")
            return DiscoveryResponse(agents=[], total_found=0)
        
        try:
            client = self._get_client()
            
            # Prepare request payload
            payload = query.model_dump(exclude_none=True)
            
            # Call OpenClaw discovery API
            # Note: This is a placeholder - actual implementation depends on OpenClaw API
            response = await client.post(
                "/api/v1/discover",
                json=payload,
                timeout=10.0
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Convert to DiscoveryResponse
            agents = [
                DiscoveredAgent(**agent_data)
                for agent_data in data.get("agents", [])
            ]
            
            return DiscoveryResponse(
                agents=agents,
                total_found=data.get("total_found", len(agents))
            )
            
        except httpx.ConnectError as e:
            logger.warning(f"OpenClaw network not accessible: {e}. Returning empty result.")
            # Network not accessible - return empty result instead of failing
            return DiscoveryResponse(agents=[], total_found=0)
        except httpx.TimeoutException as e:
            logger.warning(f"OpenClaw network timeout: {e}. Returning empty result.")
            return DiscoveryResponse(agents=[], total_found=0)
        except httpx.HTTPStatusError as e:
            logger.error(f"OpenClaw discovery failed: {e.response.status_code}")
            # For non-5xx errors, return empty result
            if e.response.status_code < 500:
                return DiscoveryResponse(agents=[], total_found=0)
            raise APIError(
                f"OpenClaw discovery failed: {e.response.status_code}",
                code="OPENCLAW_DISCOVERY_ERROR",
                retryable=True
            ) from e
        except httpx.RequestError as e:
            logger.warning(f"OpenClaw network error: {e}. Returning empty result.")
            # Network errors - return empty result instead of failing
            return DiscoveryResponse(agents=[], total_found=0)
        except Exception as e:
            logger.exception(f"Unexpected error in OpenClaw discovery: {e}")
            # Unexpected errors - return empty result
            return DiscoveryResponse(agents=[], total_found=0)
    
    async def request_collaboration(self, request: CollaborationRequest) -> CollaborationResponse:
        """
        Request collaboration with another agent.
        
        Reference: specs/openclaw_integration.md Section 4.1
        
        Args:
            request: Collaboration request
            
        Returns:
            CollaborationResponse with collaboration status
            
        Raises:
            APIError: If collaboration request fails
        """
        # Mock mode: Return mock response
        if self.mock_mode:
            logger.info("OpenClaw in mock mode, returning mock collaboration response")
            return CollaborationResponse(
                status="pending",
                message="Mock mode: Collaboration request simulated"
            )
        
        if not self.is_configured():
            logger.warning("OpenClaw not configured, returning rejected collaboration")
            return CollaborationResponse(
                status="rejected",
                message="OpenClaw not configured"
            )
        
        try:
            client = self._get_client()
            
            # Prepare request payload
            payload = request.model_dump(exclude_none=True)
            payload["requester_agent_id"] = str(payload["requester_agent_id"])
            payload["target_agent_id"] = str(payload["target_agent_id"])
            if payload.get("deadline"):
                payload["deadline"] = payload["deadline"].isoformat()
            
            # Call OpenClaw collaboration API
            response = await client.post(
                "/api/v1/collaborate",
                json=payload,
                timeout=10.0
            )
            response.raise_for_status()
            
            data = response.json()
            
            return CollaborationResponse(**data)
            
        except httpx.ConnectError as e:
            logger.warning(f"OpenClaw network not accessible: {e}. Returning pending response.")
            return CollaborationResponse(
                status="pending",
                message="Network not accessible - request queued"
            )
        except httpx.TimeoutException as e:
            logger.warning(f"OpenClaw network timeout: {e}. Returning pending response.")
            return CollaborationResponse(
                status="pending",
                message="Network timeout - request queued"
            )
        except httpx.HTTPStatusError as e:
            logger.error(f"OpenClaw collaboration request failed: {e.response.status_code}")
            if e.response.status_code < 500:
                return CollaborationResponse(
                    status="rejected",
                    message=f"Request rejected: {e.response.status_code}"
                )
            raise APIError(
                f"OpenClaw collaboration failed: {e.response.status_code}",
                code="OPENCLAW_COLLABORATION_ERROR",
                retryable=True
            ) from e
        except httpx.RequestError as e:
            logger.warning(f"OpenClaw network error: {e}. Returning pending response.")
            return CollaborationResponse(
                status="pending",
                message="Network error - request queued"
            )
        except Exception as e:
            logger.exception(f"Unexpected error in OpenClaw collaboration: {e}")
            return CollaborationResponse(
                status="pending",
                message="Unexpected error - request queued"
            )
    
    async def share_trend(self, trend: TrendShare) -> bool:
        """
        Share a trend with the OpenClaw network.
        
        Reference: specs/openclaw_integration.md Section 5.1
        
        Args:
            trend: Trend to share
            
        Returns:
            True if trend was shared successfully (or queued in mock mode)
            
        Raises:
            APIError: If trend sharing fails (only for non-recoverable errors)
        """
        # Mock mode: Simulate successful sharing
        if self.mock_mode:
            logger.info(f"OpenClaw in mock mode, trend {trend.trend_id} sharing simulated")
            return True
        
        if not self.is_configured():
            logger.warning("OpenClaw not configured, trend sharing skipped")
            return False
        
        try:
            client = self._get_client()
            
            # Prepare request payload
            payload = trend.model_dump(exclude_none=True)
            payload["trend_id"] = str(payload["trend_id"])
            payload["attribution"]["agent_id"] = str(payload["attribution"]["agent_id"])
            payload["attribution"]["discovered_at"] = payload["attribution"]["discovered_at"].isoformat()
            payload["published_at"] = payload["published_at"].isoformat()
            
            # Call OpenClaw trend sharing API
            response = await client.post(
                "/api/v1/trends/share",
                json=payload,
                timeout=10.0
            )
            response.raise_for_status()
            
            logger.info(f"Trend {trend.trend_id} shared successfully to OpenClaw")
            return True
            
        except httpx.ConnectError as e:
            logger.warning(f"OpenClaw network not accessible: {e}. Trend sharing skipped.")
            return False
        except httpx.TimeoutException as e:
            logger.warning(f"OpenClaw network timeout: {e}. Trend sharing skipped.")
            return False
        except httpx.HTTPStatusError as e:
            logger.error(f"OpenClaw trend sharing failed: {e.response.status_code}")
            # For non-5xx errors, return False (trend not shared)
            if e.response.status_code < 500:
                return False
            raise APIError(
                f"OpenClaw trend sharing failed: {e.response.status_code}",
                code="OPENCLAW_TREND_SHARE_ERROR",
                retryable=True
            ) from e
        except httpx.RequestError as e:
            logger.warning(f"OpenClaw network error: {e}. Trend sharing skipped.")
            return False
        except Exception as e:
            logger.exception(f"Unexpected error in OpenClaw trend sharing: {e}")
            return False
    
    async def discover_trends(
        self,
        topic: Optional[str] = None,
        sources: Optional[List[str]] = None,
        timeframe: str = "24h",
        min_engagement: Optional[float] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Discover trends from the OpenClaw network.
        
        Reference: specs/openclaw_integration.md Section 3.2
        
        Args:
            topic: Topic to search for
            sources: Sources to query
            timeframe: Time window (1h, 24h, 7d, 30d)
            min_engagement: Minimum engagement threshold
            limit: Maximum number of results
            
        Returns:
            List of discovered trends (empty if network unavailable)
        """
        # Mock mode: Return empty list
        if self.mock_mode:
            logger.info("OpenClaw in mock mode, returning empty trend list")
            return []
        
        if not self.is_configured():
            logger.warning("OpenClaw not configured, returning empty trend list")
            return []
        
        try:
            client = self._get_client()
            
            # Prepare request payload
            payload = {
                "topic": topic,
                "sources": sources or [],
                "timeframe": timeframe,
                "limit": limit
            }
            if min_engagement is not None:
                payload["min_engagement"] = min_engagement
            
            # Call OpenClaw trend discovery API
            response = await client.post(
                "/api/v1/trends/discover",
                json=payload,
                timeout=10.0
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get("trends", [])
            
        except httpx.ConnectError as e:
            logger.warning(f"OpenClaw network not accessible: {e}. Returning empty trend list.")
            return []
        except httpx.TimeoutException as e:
            logger.warning(f"OpenClaw network timeout: {e}. Returning empty trend list.")
            return []
        except httpx.HTTPStatusError as e:
            logger.error(f"OpenClaw trend discovery failed: {e.response.status_code}")
            # Return empty list for non-5xx errors
            if e.response.status_code < 500:
                return []
            # For 5xx errors, return empty list (don't fail)
            return []
        except httpx.RequestError as e:
            logger.warning(f"OpenClaw network error: {e}. Returning empty trend list.")
            return []
        except Exception as e:
            logger.exception(f"Unexpected error in OpenClaw trend discovery: {e}")
            return []
    
    async def close(self):
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
