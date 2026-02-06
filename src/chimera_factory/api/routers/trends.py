"""
Trend Research API endpoints.

Reference: specs/technical.md (Trend Research API section)
"""

from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from uuid import UUID, uuid4

from chimera_factory.api.models import (
    APIResponse,
    TrendResearchRequest,
    TrendResearchResponse,
    TrendItemResponse,
)
from chimera_factory.trends.models import TrendItem
from chimera_factory.skills import skill_trend_research
from chimera_factory.exceptions import TrendResearchError, RateLimitError
from chimera_factory.utils.logging import setup_logger

logger = setup_logger(__name__)

router = APIRouter()


@router.post("/research", response_model=APIResponse, status_code=status.HTTP_200_OK)
async def research_trends(request: TrendResearchRequest):
    """
    Research trends from multiple sources.
    
    Reference: specs/technical.md lines 68-239
    
    Args:
        request: Trend research request
        
    Returns:
        APIResponse with trend research results
        
    Raises:
        HTTPException: If research fails or rate limit exceeded
    """
    try:
        # Convert request to skill input format
        input_data = {
            "topic": request.topic,
            "sources": request.sources,
            "timeframe": request.timeframe,
            "agent_id": str(request.agent_id) if request.agent_id else None,
        }
        
        # Execute trend research skill
        result = skill_trend_research.execute(input_data)
        
        # Convert to API response format
        # result["trends"] is a list of TrendItem models from skill_trend_research
        # The skill already returns TrendItem models, so we can use them directly
        trend_items = result.get("trends", [])
        
        # Ensure all items are TrendItem instances
        if trend_items and isinstance(trend_items[0], dict):
            trend_items = [
                TrendItem(
                    id=UUID(item.get("id")) if item.get("id") else uuid4(),
                    title=item.get("title", ""),
                    source=item.get("source", ""),
                    engagement=item.get("engagement", 0.0),
                    timestamp=item.get("timestamp", datetime.now().isoformat()),
                    url=item.get("url"),
                    relevance_score=item.get("relevance_score"),
                    velocity=item.get("velocity"),
                    hashtags=item.get("hashtags"),
                    related_topics=item.get("related_topics"),
                )
                for item in trend_items
            ]
        
        # Extract request_id and confidence from result
        request_id = result.get("request_id")
        if request_id and isinstance(request_id, str):
            request_id = UUID(request_id)
        elif not request_id:
            request_id = uuid4()
        
        confidence = result.get("confidence", 0.0)
        
        # Create base response model
        from chimera_factory.trends.models import TrendResearchResponse as TrendResearchResponseBase
        base_response = TrendResearchResponseBase(
            trends=trend_items,
            analysis=result.get("analysis", {
                "total_trends": len(trend_items),
                "sources_queried": len(request.sources),
                "confidence": confidence
            }),
            request_id=request_id
        )
        
        # Create API response with top-level confidence
        response = TrendResearchResponse.from_base(base_response, confidence)
        
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
                "details": {"platform": e.platform, "remaining": e.remaining}
            }
        )
    
    except TrendResearchError as e:
        logger.error(f"Trend research error: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "TREND_RESEARCH_ERROR",
                "message": e.message,
                "details": {"retryable": e.retryable}
            }
        )
    
    except Exception as e:
        logger.exception(f"Unexpected error in trend research: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An error occurred during trend research",
                "details": {"type": type(e).__name__}
            }
        )
