"""
Content Generation API endpoints.

Reference: specs/technical.md (Content Generation API section)
"""

from fastapi import APIRouter, HTTPException, status
from datetime import datetime

from chimera_factory.api.models import (
    APIResponse,
    ContentGenerateRequest,
    ContentGenerateResponse,
)
from chimera_factory.skills import skill_content_generate
from chimera_factory.exceptions import ContentGenerationError, RateLimitError
from chimera_factory.utils.logging import setup_logger

logger = setup_logger(__name__)

router = APIRouter()


@router.post("/generate", response_model=APIResponse, status_code=status.HTTP_200_OK)
async def generate_content(request: ContentGenerateRequest):
    """
    Generate multimodal content (text, image, video).
    
    Reference: specs/technical.md (Content Generation API section)
    
    Args:
        request: Content generation request
        
    Returns:
        APIResponse with generated content details
        
    Raises:
        HTTPException: If generation fails or rate limit exceeded
    """
    try:
        # Convert request to skill input format
        input_data = {
            "content_type": request.content_type,
            "prompt": request.prompt,
            "style": request.style,
            "character_reference_id": str(request.character_reference_id) if request.character_reference_id else None,
            "agent_id": str(request.agent_id) if request.agent_id else None,
            "platform": request.platform,
        }
        
        # Execute content generation skill
        result = skill_content_generate.execute(input_data)
        
        # Convert to API response format
        response = ContentGenerateResponse(
            content_url=result["content_url"],
            metadata=result.get("metadata", {}),
            confidence=result.get("confidence", 0.0)
        )
        
        return APIResponse(
            success=True,
            data=response.model_dump(),
            error=None,
            timestamp=datetime.now()
        )
    
    except RateLimitError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "code": "RATE_LIMIT_EXCEEDED",
                "message": e.message,
                "details": {"remaining": e.remaining}
            }
        )
    
    except ContentGenerationError as e:
        logger.error(f"Content generation error: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "CONTENT_GENERATION_ERROR",
                "message": e.message,
                "details": {"retryable": e.retryable}
            }
        )
    
    except ValueError as e:
        # Validation errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "VALIDATION_ERROR",
                "message": str(e),
                "details": {}
            }
        )
    
    except Exception as e:
        logger.exception(f"Unexpected error in content generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An error occurred during content generation",
                "details": {"type": type(e).__name__}
            }
        )
