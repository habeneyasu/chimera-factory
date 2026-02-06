"""
Pydantic models for OpenClaw network integration.

Reference: specs/openclaw_integration.md
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, HttpUrl, ConfigDict


class AgentResources(BaseModel):
    """Agent resource metrics."""
    
    cpu_usage_percent: float = Field(..., ge=0, le=100, description="CPU usage percentage")
    memory_usage_percent: float = Field(..., ge=0, le=100, description="Memory usage percentage")
    queue_depth: int = Field(..., ge=0, description="Current queue depth")
    max_concurrent_tasks: Optional[int] = Field(None, ge=1, description="Maximum concurrent tasks")
    available_slots: Optional[int] = Field(None, ge=0, description="Available task slots")


class AgentReputation(BaseModel):
    """Agent reputation metrics."""
    
    score: float = Field(..., ge=0, le=1, description="Reputation score (0-1)")
    total_collaborations: int = Field(0, ge=0, description="Total collaborations")
    success_rate: Optional[float] = Field(None, ge=0, le=1, description="Success rate (0-1)")


class PerformanceMetrics(BaseModel):
    """Performance metrics for a capability."""
    
    avg_response_time_ms: Optional[int] = Field(None, ge=0, description="Average response time in milliseconds")
    success_rate: Optional[float] = Field(None, ge=0, le=1, description="Success rate (0-1)")
    queue_depth: Optional[int] = Field(None, ge=0, description="Current queue depth")
    total_invocations: Optional[int] = Field(None, ge=0, description="Total invocations")


class AgentCapability(BaseModel):
    """Agent capability/skill definition."""
    
    skill_id: str = Field(..., description="Skill identifier", pattern="^(trend_research|content_generation|engagement_management)$")
    skill_name: str = Field(..., description="Human-readable skill name")
    description: str = Field(..., description="What this skill can do")
    status: str = Field(..., description="Capability status", pattern="^(available|busy|unavailable)$")
    input_schema: Optional[Dict[str, Any]] = Field(None, description="JSON Schema for skill input")
    output_schema: Optional[Dict[str, Any]] = Field(None, description="JSON Schema for skill output")
    performance_metrics: Optional[PerformanceMetrics] = Field(None, description="Performance metrics")
    rate_limits: Optional[Dict[str, int]] = Field(None, description="Rate limits (requests_per_minute, requests_per_hour)")


class AgentStatus(BaseModel):
    """Agent status information."""
    
    agent_id: UUID = Field(..., description="Unique agent identifier")
    agent_name: str = Field(..., description="Human-readable agent name")
    status: str = Field(..., description="Current operational status", pattern="^(idle|researching|generating|engaging|sleeping|error)$")
    availability: str = Field(..., description="Availability for new tasks", pattern="^(available|busy|unavailable)$")
    capabilities: List[AgentCapability] = Field(..., description="Available capabilities")
    resources: AgentResources = Field(..., description="Resource metrics")
    reputation: Optional[AgentReputation] = Field(None, description="Reputation metrics")
    last_updated: datetime = Field(default_factory=datetime.now, description="Last status update timestamp")
    network_endpoint: Optional[HttpUrl] = Field(None, description="MCP endpoint for direct communication")


class StatusPublication(BaseModel):
    """Status publication payload."""
    
    agent_id: UUID = Field(..., description="Agent identifier")
    agent_name: str = Field(..., description="Agent name")
    status: str = Field(..., description="Current status")
    availability: str = Field(..., description="Availability")
    capabilities: List[AgentCapability] = Field(..., description="Capabilities")
    resources: AgentResources = Field(..., description="Resources")
    reputation: Optional[AgentReputation] = Field(None, description="Reputation")
    last_updated: datetime = Field(default_factory=datetime.now, description="Last updated")
    network_endpoint: Optional[HttpUrl] = Field(None, description="Network endpoint")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "agent_id": "123e4567-e89b-12d3-a456-426614174000",
                "agent_name": "Chimera Agent 1",
                "status": "idle",
                "availability": "available",
                "capabilities": [
                    {
                        "skill_id": "trend_research",
                        "skill_name": "Trend Research",
                        "description": "Research trending topics from multiple sources",
                        "status": "available"
                    }
                ],
                "resources": {
                    "cpu_usage_percent": 25.5,
                    "memory_usage_percent": 40.0,
                    "queue_depth": 0
                }
            }
        }
    )


class CapabilityPublication(BaseModel):
    """Capability publication payload."""
    
    agent_id: UUID = Field(..., description="Agent identifier")
    capabilities: List[AgentCapability] = Field(..., description="Capabilities")
    published_at: datetime = Field(default_factory=datetime.now, description="Publication timestamp")


class DiscoveryQuery(BaseModel):
    """Agent discovery query."""
    
    capabilities: Optional[List[str]] = Field(None, description="Required capabilities")
    status: Optional[str] = Field(None, pattern="^(idle|available)$", description="Filter by agent status")
    min_reputation: Optional[float] = Field(None, ge=0, le=1, description="Minimum reputation score")
    max_response_time_ms: Optional[int] = Field(None, ge=0, description="Maximum acceptable response time")
    limit: int = Field(10, ge=1, le=100, description="Maximum number of results")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "capabilities": ["trend_research"],
                "status": "available",
                "min_reputation": 0.7,
                "limit": 10
            }
        }
    )


class DiscoveredAgent(BaseModel):
    """Discovered agent information."""
    
    agent_id: UUID = Field(..., description="Agent identifier")
    name: str = Field(..., description="Agent name")
    capabilities: List[str] = Field(..., description="Available capabilities")
    status: str = Field(..., description="Current status")
    reputation: Optional[float] = Field(None, ge=0, le=1, description="Reputation score")
    resources: Optional[AgentResources] = Field(None, description="Resource metrics")
    network_endpoint: Optional[HttpUrl] = Field(None, description="Network endpoint")


class DiscoveryResponse(BaseModel):
    """Discovery query response."""
    
    agents: List[DiscoveredAgent] = Field(..., description="Discovered agents")
    total_found: int = Field(..., ge=0, description="Total number of agents found")
    query_id: Optional[UUID] = Field(default_factory=uuid4, description="Query identifier")


class CollaborationRequest(BaseModel):
    """Collaboration request."""
    
    requester_agent_id: UUID = Field(..., description="Requester agent identifier")
    target_agent_id: UUID = Field(..., description="Target agent identifier")
    task: str = Field(..., description="Task description")
    required_capability: str = Field(..., pattern="^(trend_research|content_generation|engagement_management)$", description="Required capability")
    input_data: Optional[Dict[str, Any]] = Field(None, description="Task input data")
    deadline: Optional[datetime] = Field(None, description="Task deadline")
    compensation: Optional[Dict[str, Any]] = Field(None, description="Compensation details")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "requester_agent_id": "123e4567-e89b-12d3-a456-426614174000",
                "target_agent_id": "223e4567-e89b-12d3-a456-426614174000",
                "task": "Research trends on AI ethics",
                "required_capability": "trend_research",
                "input_data": {
                    "topic": "AI ethics",
                    "sources": ["twitter", "news"]
                }
            }
        }
    )


class CollaborationResponse(BaseModel):
    """Collaboration response."""
    
    collaboration_id: UUID = Field(default_factory=uuid4, description="Collaboration identifier")
    status: str = Field(..., pattern="^(accepted|rejected|pending)$", description="Response status")
    response: Optional[Dict[str, Any]] = Field(None, description="Response details (estimated_completion, cost, terms)")
    message: Optional[str] = Field(None, description="Response message")


class TrendAttribution(BaseModel):
    """Trend attribution information."""
    
    agent_id: UUID = Field(..., description="Agent that discovered the trend")
    agent_name: str = Field(..., description="Agent name")
    discovered_at: datetime = Field(..., description="Discovery timestamp")


class TrendShare(BaseModel):
    """Trend sharing payload."""
    
    trend_id: UUID = Field(..., description="Trend identifier")
    title: str = Field(..., description="Trend title")
    source: str = Field(..., pattern="^(twitter|youtube|news|reddit)$", description="Trend source")
    topic: str = Field(..., description="Trend topic")
    engagement: float = Field(..., ge=0, description="Engagement metric")
    relevance_score: Optional[float] = Field(None, ge=0, le=1, description="Relevance score")
    velocity: Optional[float] = Field(None, description="Trend velocity")
    hashtags: Optional[List[str]] = Field(None, description="Related hashtags")
    attribution: TrendAttribution = Field(..., description="Attribution information")
    published_at: datetime = Field(default_factory=datetime.now, description="Publication timestamp")
