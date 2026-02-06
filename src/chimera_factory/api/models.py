"""
API request/response models matching technical specifications.

Reference: specs/technical.md (API Contracts section)
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, HttpUrl, ConfigDict

# Import trend models from trends package to avoid duplication
from chimera_factory.trends.models import TrendItem, TrendResearchResponse as TrendResearchResponseBase


class APIResponse(BaseModel):
    """Standard API response format."""
    
    success: bool = Field(description="Whether the request was successful")
    data: Optional[Any] = Field(None, description="Response data")
    error: Optional[Dict[str, Any]] = Field(None, description="Error details if failed")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")


class ErrorResponse(BaseModel):
    """Error response structure."""
    
    code: str = Field(description="Error code")
    message: str = Field(description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


# Trend Research API Models
class TrendResearchRequest(BaseModel):
    """Request model for trend research API."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "topic": "AI influencers",
                "sources": ["twitter", "news"],
                "timeframe": "24h",
                "agent_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }
    )
    
    topic: str = Field(..., min_length=1, max_length=255, description="Topic or keyword to research")
    sources: List[str] = Field(..., min_length=1, max_length=10, description="List of sources to query")
    timeframe: str = Field("24h", description="Time window for trend analysis")
    agent_id: Optional[UUID] = Field(None, description="Agent identifier")


# Re-export TrendItem as TrendItemResponse for API compatibility
TrendItemResponse = TrendItem


# Extend TrendResearchResponse to include top-level confidence for API contract
class TrendResearchResponse(TrendResearchResponseBase):
    """API response model for trend research with top-level confidence."""
    
    confidence: float = Field(..., ge=0, le=1, description="Confidence score for trend accuracy")
    
    @classmethod
    def from_base(cls, base: TrendResearchResponseBase, confidence: float):
        """Create API response from base model with confidence."""
        return cls(
            trends=base.trends,
            analysis=base.analysis,
            request_id=base.request_id,
            confidence=confidence
        )


# Content Generation API Models
class ContentGenerateRequest(BaseModel):
    """Request model for content generation API."""
    
    content_type: str = Field(..., description="Type of content to generate")
    prompt: str = Field(..., min_length=1, description="Content generation prompt")
    style: Optional[str] = Field(None, description="Persona style guide reference")
    character_reference_id: Optional[UUID] = Field(None, description="Character consistency lock ID")
    agent_id: Optional[UUID] = Field(None, description="Agent identifier")
    platform: Optional[str] = Field(None, description="Target platform")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "content_type": "image",
                "prompt": "A futuristic AI influencer",
                "style": "modern",
                "character_reference_id": "123e4567-e89b-12d3-a456-426614174000",
                "agent_id": "123e4567-e89b-12d3-a456-426614174000",
                "platform": "twitter"
            }
        }
    )


class ContentGenerateResponse(BaseModel):
    """Response model for content generation API."""
    
    content_url: HttpUrl = Field(description="URL or path to generated content")
    metadata: Dict[str, Any] = Field(description="Content metadata")
    confidence: float = Field(ge=0, le=1, description="Confidence score for content quality")


# Engagement Management API Models
class EngagementManageRequest(BaseModel):
    """Request model for engagement management API."""
    
    action: str = Field(..., description="Type of engagement action")
    platform: str = Field(..., description="Target platform")
    target: str = Field(..., min_length=1, description="Target post/comment/user ID")
    content: Optional[str] = Field(None, description="Content for reply/comment")
    persona_constraints: Optional[List[str]] = Field(None, description="Persona constraints to apply")
    agent_id: Optional[UUID] = Field(None, description="Agent identifier")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "action": "like",
                "platform": "twitter",
                "target": "tweet_12345",
                "agent_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }
    )


class EngagementManageResponse(BaseModel):
    """Response model for engagement management API."""
    
    status: str = Field(description="Engagement status")
    engagement_id: Optional[str] = Field(None, description="ID of created engagement (UUID or platform-specific ID)")
    platform_response: Optional[Dict[str, Any]] = Field(None, description="Raw response from platform API")
    error: Optional[Dict[str, Any]] = Field(None, description="Error details if status is failed")


# Agent Orchestration API Models
class AgentCreate(BaseModel):
    """Request model for creating an agent."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Agent name")
    persona_id: str = Field(..., description="Persona identifier")
    wallet_address: Optional[str] = Field(None, pattern="^0x[a-fA-F0-9]{40}$", description="Ethereum wallet address")


class Agent(BaseModel):
    """Agent model."""
    
    id: UUID = Field(description="Agent UUID")
    name: str = Field(description="Agent name")
    status: str = Field(description="Agent status")
    wallet_address: str = Field(description="Ethereum wallet address")
    persona_id: str = Field(description="Persona identifier")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")


class CampaignCreate(BaseModel):
    """Request model for creating a campaign."""
    
    goal: str = Field(..., min_length=1, description="Campaign goal")
    agent_ids: List[UUID] = Field(..., min_length=1, description="List of agent UUIDs")


class Campaign(BaseModel):
    """Campaign model."""
    
    id: UUID = Field(description="Campaign UUID")
    goal: str = Field(description="Campaign goal")
    status: str = Field(description="Campaign status")
    agent_ids: List[UUID] = Field(description="List of agent UUIDs")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
