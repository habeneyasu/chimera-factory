"""
Trend data models using Pydantic for validation.

Reference: specs/technical.md (Trend Research API)
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, field_validator


class TrendItem(BaseModel):
    """
    Trend item model matching API contract.
    
    Reference: specs/technical.md lines 152-198
    """
    id: UUID = Field(default_factory=uuid4, description="Unique trend identifier")
    title: str = Field(..., description="Trend title")
    source: str = Field(..., description="Source platform")
    engagement: float = Field(..., ge=0, description="Engagement metric (non-negative)")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    
    # Optional fields
    url: Optional[str] = Field(None, description="URL to trend source")
    relevance_score: Optional[float] = Field(None, ge=0, le=1, description="Relevance score (0-1)")
    velocity: Optional[float] = Field(None, description="Trend velocity (rate of growth)")
    hashtags: Optional[List[str]] = Field(None, description="Related hashtags")
    related_topics: Optional[List[str]] = Field(None, description="Related topics")
    attribution: Optional[dict] = Field(None, description="Attribution info (agent_id, agent_name)")
    
    @field_validator("source")
    @classmethod
    def validate_source(cls, v: str) -> str:
        """Validate source is one of the allowed values."""
        allowed_sources = ["twitter", "youtube", "news", "reddit", "openclaw"]
        if v not in allowed_sources:
            raise ValueError(f"source must be one of {allowed_sources}, got {v}")
        return v
    
    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, v: str) -> str:
        """Validate timestamp is ISO 8601 format."""
        try:
            # Try parsing ISO 8601 format
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError(f"timestamp must be ISO 8601 format, got {v}")
        return v
    
    @field_validator("engagement")
    @classmethod
    def validate_engagement(cls, v: float) -> float:
        """Validate engagement is non-negative."""
        if v < 0:
            raise ValueError(f"engagement must be non-negative, got {v}")
        return v
    
    @field_validator("relevance_score")
    @classmethod
    def validate_relevance_score(cls, v: Optional[float]) -> Optional[float]:
        """Validate relevance_score is between 0 and 1."""
        if v is not None and (v < 0 or v > 1):
            raise ValueError(f"relevance_score must be between 0 and 1, got {v}")
        return v


class TrendResearchResponse(BaseModel):
    """
    Trend research response model matching API contract.
    
    Reference: specs/technical.md lines 203-230
    """
    trends: List[TrendItem] = Field(..., description="List of trend items")
    analysis: dict = Field(..., description="Analysis metadata")
    request_id: UUID = Field(default_factory=uuid4, description="Request identifier")
    
    @field_validator("analysis")
    @classmethod
    def validate_analysis(cls, v: dict) -> dict:
        """Validate analysis has required fields."""
        if "total_trends" not in v:
            raise ValueError("analysis must contain 'total_trends'")
        if "confidence" not in v:
            raise ValueError("analysis must contain 'confidence'")
        
        # Validate confidence is between 0 and 1
        confidence = v.get("confidence")
        if confidence is not None and (confidence < 0 or confidence > 1):
            raise ValueError(f"analysis.confidence must be between 0 and 1, got {confidence}")
        
        return v
