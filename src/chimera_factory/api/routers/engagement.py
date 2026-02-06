"""
Engagement Management API endpoints.

Reference: specs/technical.md (Engagement Management API section)
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from datetime import datetime
from uuid import UUID

from chimera_factory.api.models import (
    APIResponse,
    EngagementManageRequest,
    EngagementManageResponse,
)
from chimera_factory.skills import skill_engagement_manage
from chimera_factory.exceptions import EngagementError, RateLimitError
from chimera_factory.utils.logging import setup_logger

logger = setup_logger(__name__)

router = APIRouter()


@router.post("/manage", response_model=APIResponse, status_code=status.HTTP_200_OK)
async def manage_engagement(request: EngagementManageRequest):
    """
    Manage social media engagement actions (reply, like, follow, comment, share).
    
    Reference: specs/technical.md (Engagement Management API section)
    
    Args:
        request: Engagement management request
        
    Returns:
        APIResponse with engagement result
        
    Raises:
        HTTPException: If engagement fails or rate limit exceeded
    """
    try:
        # Convert request to skill input format
        input_data = {
            "action": request.action,
            "platform": request.platform,
            "target": request.target,
            "content": request.content,
            "persona_constraints": request.persona_constraints,
            "agent_id": str(request.agent_id) if request.agent_id else None,
        }
        
        # Execute engagement management skill
        result = skill_engagement_manage.execute(input_data)
        
        # Convert to API response format
        # engagement_id can be UUID string or platform-specific ID string
        engagement_id = result.get("engagement_id")
        if engagement_id:
            engagement_id = str(engagement_id)  # Convert to string (handles UUID objects)
        
        # Clean platform_response (remove datetime objects)
        platform_response = result.get("platform_response")
        if platform_response and isinstance(platform_response, dict):
            # Recursively convert datetime objects to ISO format strings
            def clean_dict(d):
                """Recursively clean dict, converting datetime to string."""
                cleaned = {}
                for key, value in d.items():
                    if isinstance(value, datetime):
                        cleaned[key] = value.isoformat()
                    elif isinstance(value, dict):
                        cleaned[key] = clean_dict(value)
                    elif isinstance(value, list):
                        cleaned[key] = [
                            clean_dict(item) if isinstance(item, dict) else (
                                item.isoformat() if isinstance(item, datetime) else item
                            )
                            for item in value
                        ]
                    else:
                        cleaned[key] = value
                return cleaned
            platform_response = clean_dict(platform_response)
        
        response = EngagementManageResponse(
            status=result.get("status", "failed"),
            engagement_id=engagement_id,
            platform_response=platform_response,
            error=result.get("error")
        )
        
        # Determine HTTP status based on engagement status
        http_status = status.HTTP_200_OK
        if result.get("status") == "failed":
            http_status = status.HTTP_400_BAD_REQUEST
        
        # Use model_dump with mode='json' to handle datetime serialization
        response_data = response.model_dump(mode='json')
        
        return JSONResponse(
            status_code=http_status,
            content=APIResponse(
                success=result.get("status") == "success",
                data=response_data,
                error=result.get("error"),
                timestamp=datetime.now()
            ).model_dump(mode='json')
        )
    
    except RateLimitError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "code": "RATE_LIMIT_EXCEEDED",
                "message": e.message,
                "details": {"platform": e.platform, "remaining": e.remaining}
            }
        )
    
    except EngagementError as e:
        logger.error(f"Engagement error: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "ENGAGEMENT_ERROR",
                "message": e.message,
                "details": {"retryable": e.retryable}
            }
        )
    
    except Exception as e:
        logger.exception(f"Unexpected error in engagement management: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An error occurred during engagement management",
                "details": {"type": type(e).__name__}
            }
        )
