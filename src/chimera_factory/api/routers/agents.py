"""
Agent Orchestration API endpoints.

Reference: specs/api/orchestrator.yaml
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from datetime import datetime
from uuid import UUID, uuid4

from chimera_factory.api.models import APIResponse, AgentCreate
from chimera_factory.db import get_db_connection, get_agent_by_id
from chimera_factory.utils.logging import setup_logger

logger = setup_logger(__name__)

router = APIRouter()


@router.get("", response_model=APIResponse, status_code=status.HTTP_200_OK)
async def list_agents():
    """
    List all agents.
    
    Reference: specs/api/orchestrator.yaml (GET /agents)
    
    Returns:
        APIResponse with list of agents
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM agents ORDER BY created_at DESC")
                rows = cur.fetchall()
                
                agents = []
                for row in rows:
                    agents.append({
                        "id": str(row[0]),
                        "name": row[1],
                        "persona_id": row[2],
                        "wallet_address": row[3],
                        "status": row[4],
                        "created_at": row[5].isoformat() if row[5] else None,
                        "updated_at": row[6].isoformat() if row[6] else None,
                    })
        
        return APIResponse(
            success=True,
            data=agents,
            error=None,
            timestamp=datetime.now()
        )
    
    except Exception as e:
        logger.exception(f"Error listing agents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Failed to list agents",
                "details": {"type": type(e).__name__}
            }
        )


@router.post("", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(request: AgentCreate):
    """
    Create a new agent.
    
    Reference: specs/api/orchestrator.yaml (POST /agents)
    
    Args:
        request: Agent creation request
        
    Returns:
        APIResponse with created agent
    """
    try:
        agent_id = uuid4()
        
        # Generate wallet address if not provided
        wallet_address = request.wallet_address
        if not wallet_address:
            # Generate unique wallet address (simple implementation)
            import hashlib
            wallet_hash = hashlib.sha256(f"{request.name}{request.persona_id}".encode()).hexdigest()[:40]
            wallet_address = f"0x{wallet_hash}"
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        cur.execute("""
                            INSERT INTO agents (id, name, persona_id, wallet_address, status)
                            VALUES (%s, %s, %s, %s, %s)
                            RETURNING id, name, persona_id, wallet_address, status, created_at, updated_at
                        """, (
                            str(agent_id),
                            request.name,
                            request.persona_id,
                            wallet_address,
                            "sleeping"
                        ))
                        row = cur.fetchone()
                        break  # Success
                    except Exception as e:
                        if ("duplicate key" in str(e).lower() or "unique constraint" in str(e).lower()) and attempt < max_retries - 1:
                            # Wallet address conflict - generate new one
                            import hashlib
                            wallet_hash = hashlib.sha256(f"{request.name}{request.persona_id}{agent_id}{attempt}".encode()).hexdigest()[:40]
                            wallet_address = f"0x{wallet_hash}"
                            conn.rollback()  # Rollback failed transaction
                        else:
                            raise
                
                agent = {
                    "id": str(row[0]),
                    "name": row[1],
                    "persona_id": row[2],
                    "wallet_address": row[3],
                    "status": row[4],
                    "created_at": row[5].isoformat() if row[5] else None,
                    "updated_at": row[6].isoformat() if row[6] else None,
                }
        
        return APIResponse(
            success=True,
            data=agent,
            error=None,
            timestamp=datetime.now()
        )
    
    except Exception as e:
        logger.exception(f"Error creating agent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Failed to create agent",
                "details": {"type": type(e).__name__}
            }
        )


@router.get("/{agent_id}", response_model=APIResponse, status_code=status.HTTP_200_OK)
async def get_agent(agent_id: UUID):
    """
    Get agent details.
    
    Reference: specs/api/orchestrator.yaml (GET /agents/{agent_id})
    
    Args:
        agent_id: Agent UUID
        
    Returns:
        APIResponse with agent details
        
    Raises:
        HTTPException: If agent not found
    """
    try:
        agent_data = get_agent_by_id(agent_id)
        
        if not agent_data:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=APIResponse(
                    success=False,
                    data=None,
                    error={
                        "code": "NOT_FOUND",
                        "message": f"Agent {agent_id} not found",
                        "details": {}
                    },
                    timestamp=datetime.now()
                ).model_dump(mode='json')
            )
        
        return APIResponse(
            success=True,
            data=agent_data,
            error=None,
            timestamp=datetime.now()
        )
    
    except Exception as e:
        logger.exception(f"Error getting agent: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=APIResponse(
                success=False,
                data=None,
                error={
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to get agent",
                    "details": {"type": type(e).__name__}
                },
                timestamp=datetime.now()
            ).model_dump(mode='json')
        )
