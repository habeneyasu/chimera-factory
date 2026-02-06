"""
OpenClaw Network Integration API endpoints.

Reference: specs/technical.md (OpenClaw Integration API section)
"""

from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from uuid import UUID
from typing import Optional

from chimera_factory.api.models import (
    APIResponse,
    OpenClawPublishRequest,
    OpenClawPublishResponse,
    OpenClawDiscoverRequest,
    OpenClawCollaborateRequest,
)
from chimera_factory.openclaw.models import (
    DiscoveryQuery,
    DiscoveryResponse,
    CollaborationRequest,
    CollaborationResponse,
    TrendShare,
)
from chimera_factory.openclaw.service import OpenClawService
from chimera_factory.openclaw.status_service import OpenClawStatusService
from chimera_factory.exceptions import APIError, ValidationError
from chimera_factory.utils.logging import setup_logger

logger = setup_logger(__name__)

router = APIRouter()
_openclaw_service: Optional[OpenClawService] = None


def get_openclaw_service() -> OpenClawService:
    """
    Get or create OpenClaw service instance.
    
    Note: OpenClaw network may not be accessible. The service will handle
    network unavailability gracefully by returning empty results or mock responses.
    """
    global _openclaw_service
    if _openclaw_service is None:
        # Enable mock mode if network URL is not accessible or not configured
        import os
        mock_mode = os.getenv("OPENCLAW_MOCK_MODE", "false").lower() == "true"
        _openclaw_service = OpenClawService(mock_mode=mock_mode)
    return _openclaw_service


@router.post("/publish", response_model=APIResponse, status_code=status.HTTP_200_OK)
async def publish_status(request: OpenClawPublishRequest):
    """
    Publish agent capabilities and status to OpenClaw network.
    
    Reference: specs/technical.md Section 6 (POST /api/v1/openclaw/publish)
    Reference: specs/openclaw_integration.md Section 1
    
    Args:
        request: Status publication request
        
    Returns:
        APIResponse with publication result
    """
    try:
        service = get_openclaw_service()
        status_service = OpenClawStatusService(request.agent_id, service)
        
        # Publish full status
        success = await status_service.publish_full_status()
        
        response = OpenClawPublishResponse(
            agent_id=request.agent_id,
            published_at=datetime.now(),
            network_reachable=service.is_configured() and success
        )
        
        return APIResponse(
            success=True,
            data=response.model_dump(),
            error=None,
            timestamp=datetime.now()
        )
        
    except ValidationError as e:
        logger.warning(f"Validation error in OpenClaw publish: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=APIResponse(
                success=False,
                error={
                    "code": e.code,
                    "message": e.message,
                    "details": {"field": e.field}
                },
                timestamp=datetime.now()
            ).model_dump()
        )
    except APIError as e:
        logger.error(f"OpenClaw publish error: {e.message}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=APIResponse(
                success=False,
                error={
                    "code": e.code,
                    "message": e.message,
                    "details": {"retryable": e.retryable}
                },
                timestamp=datetime.now()
            ).model_dump()
        )
    except Exception as e:
        logger.exception(f"Unexpected error in OpenClaw publish: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=APIResponse(
                success=False,
                error={
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred during status publication",
                    "details": {"type": type(e).__name__}
                },
                timestamp=datetime.now()
            ).model_dump()
        )


@router.post("/discover", response_model=APIResponse, status_code=status.HTTP_200_OK)
async def discover_agents(request: OpenClawDiscoverRequest):
    """
    Discover other agents in the OpenClaw network.
    
    Reference: specs/technical.md Section 6 (POST /api/v1/openclaw/discover)
    Reference: specs/openclaw_integration.md Section 3.1
    
    Args:
        request: Discovery query request
        
    Returns:
        APIResponse with discovered agents
    """
    try:
        service = get_openclaw_service()
        
        # Convert request to DiscoveryQuery
        query = DiscoveryQuery(
            capabilities=request.capabilities,
            status=request.status,
            min_reputation=request.min_reputation,
            limit=request.limit
        )
        
        # Discover agents
        result = await service.discover_agents(query)
        
        return APIResponse(
            success=True,
            data=result.model_dump(),
            error=None,
            timestamp=datetime.now()
        )
        
    except ValidationError as e:
        logger.warning(f"Validation error in OpenClaw discover: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=APIResponse(
                success=False,
                error={
                    "code": e.code,
                    "message": e.message,
                    "details": {"field": e.field}
                },
                timestamp=datetime.now()
            ).model_dump()
        )
    except APIError as e:
        logger.error(f"OpenClaw discover error: {e.message}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=APIResponse(
                success=False,
                error={
                    "code": e.code,
                    "message": e.message,
                    "details": {"retryable": e.retryable}
                },
                timestamp=datetime.now()
            ).model_dump()
        )
    except Exception as e:
        logger.exception(f"Unexpected error in OpenClaw discover: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=APIResponse(
                success=False,
                error={
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred during agent discovery",
                    "details": {"type": type(e).__name__}
                },
                timestamp=datetime.now()
            ).model_dump()
        )


@router.post("/collaborate", response_model=APIResponse, status_code=status.HTTP_200_OK)
async def request_collaboration(request: OpenClawCollaborateRequest):
    """
    Request collaboration with another agent.
    
    Reference: specs/technical.md Section 6 (POST /api/v1/openclaw/collaborate)
    Reference: specs/openclaw_integration.md Section 4.1
    
    Args:
        request: Collaboration request
        
    Returns:
        APIResponse with collaboration response
    """
    try:
        service = get_openclaw_service()
        
        # Convert request to CollaborationRequest
        collab_request = CollaborationRequest(
            requester_agent_id=request.requester_agent_id,
            target_agent_id=request.target_agent_id,
            task=request.task,
            required_capability=request.required_capability,
            input_data=request.input_data,
            deadline=request.deadline,
            compensation=request.compensation
        )
        
        # Request collaboration
        result = await service.request_collaboration(collab_request)
        
        return APIResponse(
            success=True,
            data=result.model_dump(),
            error=None,
            timestamp=datetime.now()
        )
        
    except ValidationError as e:
        logger.warning(f"Validation error in OpenClaw collaborate: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=APIResponse(
                success=False,
                error={
                    "code": e.code,
                    "message": e.message,
                    "details": {"field": e.field}
                },
                timestamp=datetime.now()
            ).model_dump()
        )
    except APIError as e:
        logger.error(f"OpenClaw collaborate error: {e.message}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=APIResponse(
                success=False,
                error={
                    "code": e.code,
                    "message": e.message,
                    "details": {"retryable": e.retryable}
                },
                timestamp=datetime.now()
            ).model_dump()
        )
    except Exception as e:
        logger.exception(f"Unexpected error in OpenClaw collaborate: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=APIResponse(
                success=False,
                error={
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred during collaboration request",
                    "details": {"type": type(e).__name__}
                },
                timestamp=datetime.now()
            ).model_dump()
        )
