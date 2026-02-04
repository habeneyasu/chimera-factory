"""
Executable Skill Contracts: Project Chimera

This module provides Pydantic models for all skill contracts, ensuring
machine-readable and validated interfaces.

Prepared By: habeneyasu
Repository: https://github.com/habeneyasu/chimera-factory
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field


# Base Skill Models
class SkillInput(BaseModel):
    """Base input contract for skill execution"""
    pass


class SkillOutput(BaseModel):
    """Base output contract for skill execution"""
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score (0.0 to 1.0)")


class SkillError(Exception):
    """Base exception for skill errors"""
    pass


# Trend Research Skill
class TrendItem(BaseModel):
    """Individual trend item"""
    title: str
    source: str
    engagement: float = Field(ge=0, description="Engagement metric")
    timestamp: str = Field(description="ISO 8601 timestamp")


class TrendResearchInput(SkillInput):
    """Input contract for trend research skill"""
    topic: str = Field(description="Topic or keyword to research")
    sources: List[Literal["twitter", "news", "reddit"]] = Field(
        min_length=1,
        description="List of sources to query"
    )
    timeframe: Literal["1h", "24h", "7d", "30d"] = Field(
        default="24h",
        description="Time window for trend analysis"
    )


class TrendResearchOutput(SkillOutput):
    """Output contract for trend research skill"""
    trends: List[TrendItem] = Field(min_length=0)


# Content Generation Skill
class ContentMetadata(BaseModel):
    """Metadata for generated content"""
    platform: Optional[str] = None
    format: Optional[str] = None
    dimensions: Optional[dict] = None
    duration: Optional[float] = None  # For video content


class ContentGenerateInput(SkillInput):
    """Input contract for content generation skill"""
    content_type: Literal["text", "image", "video", "multimodal"] = Field(
        description="Type of content to generate"
    )
    prompt: str = Field(description="Content generation prompt")
    style: Optional[str] = Field(None, description="Persona style guide reference")
    character_reference_id: Optional[str] = Field(
        None,
        description="Character consistency lock ID"
    )


class ContentGenerateOutput(SkillOutput):
    """Output contract for content generation skill"""
    content_url: str = Field(description="URL or path to generated content")
    metadata: ContentMetadata


# Engagement Management Skill
class EngagementManageInput(SkillInput):
    """Input contract for engagement management skill"""
    action: Literal["reply", "like", "follow", "comment", "share"] = Field(
        description="Engagement action to perform"
    )
    platform: Literal["twitter", "instagram", "tiktok", "threads"] = Field(
        description="Target platform"
    )
    target: str = Field(description="Target post/comment/user ID")
    content: Optional[str] = Field(None, description="Content for reply/comment")
    persona_constraints: Optional[List[str]] = Field(
        None,
        description="Persona constraints to apply"
    )


class EngagementManageOutput(SkillOutput):
    """Output contract for engagement management skill"""
    status: Literal["success", "pending", "failed"] = Field(
        description="Engagement status"
    )
    engagement_id: Optional[str] = Field(None, description="ID of created engagement")
    platform_response: Optional[dict] = Field(
        None,
        description="Raw response from platform API"
    )
