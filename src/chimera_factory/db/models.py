"""
Database model operations for Project Chimera.

Reference: specs/database/schema.sql
"""

import json
from typing import Dict, Any, Optional, List
from uuid import UUID, uuid4
from psycopg2.extras import RealDictCursor

from .connection import get_db_connection
from chimera_factory.exceptions import DatabaseError


def save_trend(
    title: str,
    source: str,
    engagement: float,
    timestamp: str,
    agent_id: Optional[str] = None,
    url: Optional[str] = None,
    relevance_score: Optional[float] = None,
    velocity: Optional[float] = None,
    hashtags: Optional[List[str]] = None,
    related_topics: Optional[List[str]] = None,
) -> UUID:
    """
    Save a trend to the database.
    
    Note: Trends are currently stored as UUIDs for future persistence.
    A trends table should be added to the schema for full persistence.
    
    Args:
        title: Trend title
        source: Source platform
        engagement: Engagement metric
        timestamp: ISO 8601 timestamp
        agent_id: Optional agent ID
        url: Optional URL
        relevance_score: Optional relevance score (0-1)
        velocity: Optional trend velocity
        hashtags: Optional list of hashtags
        related_topics: Optional list of related topics
        
    Returns:
        UUID of saved trend
        
    Raises:
        DatabaseError: If database operation fails
    """
    # For now, return UUID for future persistence
    # TODO: Add trends table to schema or use existing content_plan_trends
    # When implemented, store trend data in database
    return uuid4()


def save_content_plan(
    agent_id: UUID,
    content_type: str,
    platform: str,
    confidence_score: float,
    target_audience: Optional[str] = None,
    structure: Optional[Dict[str, Any]] = None,
    key_messages: Optional[list] = None,
) -> UUID:
    """
    Save a content plan to the database.
    
    Reference: specs/database/schema.sql (content_plans table)
    
    Args:
        agent_id: Agent UUID
        content_type: Type of content (text, image, video, multimodal)
        platform: Target platform
        confidence_score: Confidence score (0-1)
        target_audience: Optional target audience
        structure: Optional content structure (JSONB)
        key_messages: Optional key messages (JSONB)
        
    Returns:
        UUID of saved content plan
    """
    """
    Save a content plan to the database.
    
    Reference: specs/database/schema.sql (content_plans table)
    
    Args:
        agent_id: Agent UUID
        content_type: Type of content (text, image, video, multimodal)
        platform: Target platform
        confidence_score: Confidence score (0-1)
        target_audience: Optional target audience
        structure: Optional content structure (JSONB)
        key_messages: Optional key messages (JSONB)
        
    Returns:
        UUID of saved content plan
        
    Raises:
        DatabaseError: If database operation fails
    """
    plan_id = uuid4()
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO content_plans (
                        id, agent_id, content_type, platform, confidence_score,
                        target_audience, structure, key_messages, approval_status
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    str(plan_id),
                    str(agent_id),
                    content_type,
                    platform,
                    confidence_score,
                    target_audience,
                    json.dumps(structure) if structure else None,
                    json.dumps(key_messages) if key_messages else None,
                    "pending"
                ))
                result = cur.fetchone()
                if not result:
                    raise DatabaseError("Failed to save content plan", code="SAVE_FAILED")
                return UUID(result[0])
    except Exception as e:
        if isinstance(e, DatabaseError):
            raise
        raise DatabaseError(f"Database error saving content plan: {e}", code="DB_ERROR") from e


def save_content(
    plan_id: UUID,
    agent_id: UUID,
    content_type: str,
    content_url: str,
    metadata: Dict[str, Any],
    confidence_score: float,
    status: str = "pending",
) -> UUID:
    """
    Save generated content to the database.
    
    Reference: specs/database/schema.sql (content table)
    
    Args:
        plan_id: Content plan UUID
        agent_id: Agent UUID
        content_type: Type of content
        content_url: URL to content
        metadata: Content metadata (JSONB)
        confidence_score: Confidence score (0-1)
        status: Content status (pending, approved, rejected, published)
        
    Returns:
        UUID of saved content
        
    Raises:
        DatabaseError: If database operation fails
    """
    content_id = uuid4()
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO content (
                        id, plan_id, agent_id, content_type, content_url,
                        metadata, confidence_score, status
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    str(content_id),
                    str(plan_id),
                    str(agent_id),
                    content_type,
                    content_url,
                    json.dumps(metadata) if metadata else None,
                    confidence_score,
                    status
                ))
                result = cur.fetchone()
                if not result:
                    raise DatabaseError("Failed to save content", code="SAVE_FAILED")
                return UUID(result[0])
    except Exception as e:
        if isinstance(e, DatabaseError):
            raise
        raise DatabaseError(f"Database error saving content: {e}", code="DB_ERROR") from e


def save_engagement(
    agent_id: UUID,
    platform: str,
    action: str,
    target_id: str,
    status: str,
    platform_response: Optional[Dict[str, Any]] = None,
    content_id: Optional[UUID] = None,
) -> UUID:
    """
    Save engagement action to the database.
    
    Reference: specs/database/schema.sql (engagements table)
    
    Args:
        agent_id: Agent UUID
        platform: Platform name
        action: Action type (reply, like, follow, comment, share)
        target_id: Target post/comment/user ID
        status: Engagement status
        platform_response: Optional platform response (JSONB)
        content_id: Optional related content UUID
        
    Returns:
        UUID of saved engagement
        
    Raises:
        DatabaseError: If database operation fails
    """
    engagement_id = uuid4()
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO engagements (
                        id, agent_id, platform, action, target_id,
                        status, platform_response, content_id
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    str(engagement_id),
                    str(agent_id),
                    platform,
                    action,
                    target_id,
                    status,
                    json.dumps(platform_response) if platform_response else None,
                    str(content_id) if content_id else None
                ))
                result = cur.fetchone()
                if not result:
                    raise DatabaseError("Failed to save engagement", code="SAVE_FAILED")
                return UUID(result[0])
    except Exception as e:
        if isinstance(e, DatabaseError):
            raise
        raise DatabaseError(f"Database error saving engagement: {e}", code="DB_ERROR") from e


def get_agent_by_id(agent_id: UUID) -> Optional[Dict[str, Any]]:
    """
    Get agent by ID from database.
    
    Reference: specs/database/schema.sql (agents table)
    
    Args:
        agent_id: Agent UUID
        
    Returns:
        Agent data as dict or None if not found
    """
    """
    Get agent by ID from database.
    
    Reference: specs/database/schema.sql (agents table)
    
    Args:
        agent_id: Agent UUID
        
    Returns:
        Agent data as dict or None if not found
        
    Raises:
        DatabaseError: If database operation fails
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM agents WHERE id = %s
                """, (str(agent_id),))
                result = cur.fetchone()
                if result:
                    return dict(result)
        return None
    except Exception as e:
        raise DatabaseError(f"Database error getting agent: {e}", code="DB_ERROR") from e
