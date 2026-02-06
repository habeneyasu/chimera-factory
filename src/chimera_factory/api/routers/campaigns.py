"""
Campaign API endpoints.

Reference: specs/api/orchestrator.yaml
"""

from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from uuid import uuid4

from chimera_factory.api.models import APIResponse, CampaignCreate
from chimera_factory.db import get_db_connection
from chimera_factory.utils.logging import setup_logger

logger = setup_logger(__name__)

router = APIRouter()


@router.post("", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(request: CampaignCreate):
    """
    Create a new campaign.
    
    Reference: specs/api/orchestrator.yaml (POST /campaigns)
    
    Args:
        request: Campaign creation request
        
    Returns:
        APIResponse with created campaign
    """
    try:
        campaign_id = uuid4()
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Create campaign
                cur.execute("""
                    INSERT INTO campaigns (id, goal, status)
                    VALUES (%s, %s, %s)
                    RETURNING id, goal, status, created_at, updated_at
                """, (
                    str(campaign_id),
                    request.goal,
                    "active"
                ))
                row = cur.fetchone()
                
                # Associate agents with campaign
                for agent_id in request.agent_ids:
                    cur.execute("""
                        INSERT INTO campaign_agents (campaign_id, agent_id)
                        VALUES (%s, %s)
                    """, (str(campaign_id), str(agent_id)))
                
                campaign = {
                    "id": str(row[0]),
                    "goal": row[1],
                    "status": row[2],
                    "agent_ids": [str(agent_id) for agent_id in request.agent_ids],
                    "created_at": row[3].isoformat() if row[3] else None,
                    "updated_at": row[4].isoformat() if row[4] else None,
                }
        
        return APIResponse(
            success=True,
            data=campaign,
            error=None,
            timestamp=datetime.now()
        )
    
    except Exception as e:
        logger.exception(f"Error creating campaign: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Failed to create campaign",
                "details": {"type": type(e).__name__}
            }
        )
