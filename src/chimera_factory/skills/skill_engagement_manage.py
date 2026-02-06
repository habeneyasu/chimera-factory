"""
Engagement Management Skill

This skill manages social media engagement actions (reply, like, follow, comment, share)
with real platform APIs, rate limiting, and database persistence.

Reference:
- specs/functional.md US-011, US-012, US-013
- specs/technical.md (Engagement Management API)
- skills/skill_engagement_manage/README.md
- skills/skill_engagement_manage/contract.json
"""

from typing import Dict, Any
from uuid import uuid4

from ._validation import (
    validate_required_field,
    validate_string_field,
    validate_enum_field,
    validate_list_field,
    validate_string_list_items,
)

from chimera_factory.api_clients import (
    TwitterEngagementClient,
    InstagramClient,
    TikTokClient
)
from chimera_factory.utils import check_rate_limit, log_action, audit_log
from chimera_factory.db import save_engagement

# Constants
VALID_ACTIONS = ["reply", "like", "follow", "comment", "share"]
VALID_PLATFORMS = ["twitter", "instagram", "tiktok", "threads"]

# API clients
_twitter_client = TwitterEngagementClient()
_instagram_client = InstagramClient()
_tiktok_client = TikTokClient()


def execute(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute engagement management skill with real APIs, rate limiting, and database persistence.
    
    Input Contract (from contract.json):
    - action (string, required): Type of action ["reply", "like", "follow", "comment", "share"]
    - platform (string, required): Target platform ["twitter", "instagram", "tiktok", "threads"]
    - target (string, required): Target post/comment/user ID
    - content (string, optional): Content for reply/comment (required for reply/comment actions)
    - persona_constraints (array, optional): Persona constraints to apply
    - agent_id (string, optional): Agent identifier
    
    Output Contract (from contract.json):
    - status (string): Status ["success", "pending", "failed"]
    - engagement_id (string, optional): ID of created engagement (if successful)
    - platform_response (object, optional): Raw response from platform API
    - error (object, optional): Error details (if status is failed)
    
    Reference: skills/skill_engagement_manage/contract.json
    """
    # Validate required fields
    validate_required_field(input_data, "action")
    validate_required_field(input_data, "platform")
    validate_required_field(input_data, "target")
    
    action = input_data["action"]
    platform = input_data["platform"]
    target = input_data["target"]
    content = input_data.get("content")
    persona_constraints = input_data.get("persona_constraints", [])
    agent_id = input_data.get("agent_id", str(uuid4()))
    
    # Validate field types and constraints
    validate_enum_field(action, "action", VALID_ACTIONS)
    validate_enum_field(platform, "platform", VALID_PLATFORMS)
    validate_string_field(target, "target", min_length=1)
    
    # Validate persona_constraints if provided
    if persona_constraints:
        validate_list_field(persona_constraints, "persona_constraints")
        validate_string_list_items(persona_constraints, "persona_constraints")
    
    # Check if content is required for reply/comment actions
    if action in ["reply", "comment"]:
        if not content or not isinstance(content, str) or len(content) < 1:
            return {
                "status": "failed",
                "error": {
                    "code": "MISSING_CONTENT",
                    "message": f"content is required for {action} action",
                    "retryable": False
                }
            }
    
    # Log action
    log_action("engagement_manage", agent_id, {
        "action": action,
        "platform": platform,
        "target": target
    })
    
    # Check rate limit
    is_allowed, remaining = check_rate_limit(platform, agent_id)
    if not is_allowed:
        return {
            "status": "failed",
            "error": {
                "code": "RATE_LIMIT_EXCEEDED",
                "message": f"Rate limit exceeded for {platform}. Remaining: {remaining}",
                "retryable": True
            }
        }
    
    # Execute engagement action via platform API
    platform_response = None
    engagement_id = None
    
    try:
        if platform == "twitter" or platform == "threads":
            if action == "reply":
                platform_response = _twitter_client.reply(target, content)
            elif action == "like":
                platform_response = _twitter_client.like(target)
            elif action == "follow":
                platform_response = _twitter_client.follow(target)
            else:
                raise ValueError(f"Unsupported action {action} for {platform}")
        
        elif platform == "instagram":
            if action == "comment":
                platform_response = _instagram_client.comment(target, content)
            elif action == "like":
                platform_response = _instagram_client.like(target)
            else:
                raise ValueError(f"Unsupported action {action} for {platform}")
        
        elif platform == "tiktok":
            if action == "comment":
                platform_response = _tiktok_client.comment(target, content)
            elif action == "like":
                platform_response = _tiktok_client.like(target)
            else:
                raise ValueError(f"Unsupported action {action} for {platform}")
        
        engagement_id = platform_response.get("engagement_id", str(uuid4()))
        
        # Save to database
        try:
            from uuid import UUID
            db_engagement_id = save_engagement(
                agent_id=UUID(agent_id) if isinstance(agent_id, str) else agent_id,
                platform=platform,
                action=action,
                target_id=target,
                status="success",
                platform_response=platform_response
            )
            engagement_id = str(db_engagement_id)
            
            audit_log(
                "engagement_created",
                agent_id=agent_id,
                resource_type="engagement",
                resource_id=engagement_id,
                metadata={"action": action, "platform": platform, "target": target}
            )
        except Exception as e:
            # Log error but continue
            log_action("engagement_save_error", agent_id, {"error": str(e)})
        
        return {
            "status": "success",
            "engagement_id": engagement_id,
            "platform_response": platform_response
        }
    
    except Exception as e:
        # Save failed engagement to database
        try:
            from uuid import UUID
            save_engagement(
                agent_id=UUID(agent_id) if isinstance(agent_id, str) else agent_id,
                platform=platform,
                action=action,
                target_id=target,
                status="failed",
                platform_response={"error": str(e)}
            )
        except Exception:
            pass
        
        return {
            "status": "failed",
            "error": {
                "code": "API_ERROR",
                "message": str(e),
                "retryable": True
            }
        }
