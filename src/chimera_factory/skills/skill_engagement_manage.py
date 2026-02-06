"""
Engagement Management Skill

This skill manages social media engagement actions (reply, like, follow, comment, share).

Reference:
- specs/functional.md US-011, US-012, US-013
- specs/technical.md (Engagement Management API)
- skills/skill_engagement_manage/README.md
- skills/skill_engagement_manage/contract.json
"""

from typing import Dict, Any
from uuid import uuid4
from datetime import datetime

from ._validation import (
    validate_required_field,
    validate_string_field,
    validate_enum_field,
    validate_list_field,
    validate_string_list_items,
)

# Constants
VALID_ACTIONS = ["reply", "like", "follow", "comment", "share"]
VALID_PLATFORMS = ["twitter", "instagram", "tiktok", "threads"]


def execute(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute engagement management skill.
    
    Input Contract (from contract.json):
    - action (string, required): Type of action ["reply", "like", "follow", "comment", "share"]
    - platform (string, required): Target platform ["twitter", "instagram", "tiktok", "threads"]
    - target (string, required): Target post/comment/user ID
    - content (string, optional): Content for reply/comment (required for reply/comment actions)
    - persona_constraints (array, optional): Persona constraints to apply
    
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
    
    # Generate mock engagement data matching the contract
    # TODO: Replace with actual platform API calls (Twitter, Instagram, TikTok, Threads)
    if target.startswith("invalid_"):
        return {
            "status": "failed",
            "error": {
                "code": "INVALID_TARGET",
                "message": f"Target {target} is invalid",
                "retryable": False
            }
        }
    
    engagement_id = str(uuid4())
    platform_response = {
        "platform": platform,
        "action": action,
        "target": target,
        "timestamp": datetime.now().isoformat()
    }
    
    if action in ["reply", "comment"] and content:
        platform_response["content"] = content
    
    return {
        "status": "success",
        "engagement_id": engagement_id,
        "platform_response": platform_response
    }
