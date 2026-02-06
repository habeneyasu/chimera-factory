"""
Integration tests for OpenClaw network integration.

Reference: specs/openclaw_integration.md
"""

import pytest
from uuid import uuid4, UUID
from datetime import datetime
from fastapi.testclient import TestClient

from chimera_factory.api import app
from chimera_factory.db import get_db_connection, reset_connection_pool

client = TestClient(app)


@pytest.fixture(autouse=True, scope="function")
def reset_db_pool():
    """Reset database connection pool before each test."""
    reset_connection_pool()
    yield


@pytest.fixture
def test_agent_id():
    """Create a test agent for OpenClaw tests."""
    agent_id = uuid4()
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO agents (id, name, persona_id, wallet_address, status)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                str(agent_id),
                "Test OpenClaw Agent",
                "test_persona",
                f"0x{str(agent_id).replace('-', '').ljust(40, '0')}",
                "idle"
            ))
            conn.commit()
    yield agent_id
    # Cleanup
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM agents WHERE id = %s", (str(agent_id),))
            conn.commit()


@pytest.mark.integration
class TestOpenClawPublish:
    """Test OpenClaw status publication."""
    
    def test_publish_status_success(self, test_agent_id):
        """Test successful status publication."""
        response = client.post(
            "/api/v1/openclaw/publish",
            json={
                "agent_id": str(test_agent_id),
                "capabilities": ["trend_research", "content_generation"],
                "status": "idle",
                "resources": {
                    "cpu_usage": 25.0,
                    "memory_usage": 40.0,
                    "queue_depth": 0
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert data["data"]["agent_id"] == str(test_agent_id)
        assert "publication_id" in data["data"]
        assert "published_at" in data["data"]
        assert "network_reachable" in data["data"]
    
    def test_publish_status_invalid_status(self, test_agent_id):
        """Test status publication with invalid status."""
        response = client.post(
            "/api/v1/openclaw/publish",
            json={
                "agent_id": str(test_agent_id),
                "capabilities": ["trend_research"],
                "status": "invalid_status"  # Invalid
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_publish_status_missing_agent(self):
        """Test status publication with non-existent agent."""
        fake_id = uuid4()
        response = client.post(
            "/api/v1/openclaw/publish",
            json={
                "agent_id": str(fake_id),
                "capabilities": ["trend_research"],
                "status": "idle"
            }
        )
        
        # May succeed but network_reachable should be False if agent not found
        assert response.status_code in [200, 400, 404]
        if response.status_code == 200:
            data = response.json()
            # Should handle gracefully
            assert "data" in data


@pytest.mark.integration
class TestOpenClawDiscovery:
    """Test OpenClaw agent discovery."""
    
    def test_discover_agents_basic(self):
        """Test basic agent discovery."""
        response = client.post(
            "/api/v1/openclaw/discover",
            json={
                "capabilities": ["trend_research"],
                "limit": 10
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "agents" in data["data"]
        assert "total_found" in data["data"]
        assert isinstance(data["data"]["agents"], list)
        assert isinstance(data["data"]["total_found"], int)
    
    def test_discover_agents_with_filters(self):
        """Test agent discovery with filters."""
        response = client.post(
            "/api/v1/openclaw/discover",
            json={
                "capabilities": ["trend_research", "content_generation"],
                "status": "available",
                "min_reputation": 0.7,
                "limit": 5
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "agents" in data["data"]
    
    def test_discover_agents_invalid_status(self):
        """Test discovery with invalid status filter."""
        response = client.post(
            "/api/v1/openclaw/discover",
            json={
                "status": "invalid_status",  # Invalid
                "limit": 10
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_discover_agents_limit_validation(self):
        """Test discovery with invalid limit."""
        response = client.post(
            "/api/v1/openclaw/discover",
            json={
                "limit": 200  # Exceeds max of 100
            }
        )
        
        assert response.status_code == 422  # Validation error


@pytest.mark.integration
class TestOpenClawCollaboration:
    """Test OpenClaw collaboration requests."""
    
    def test_request_collaboration_success(self, test_agent_id):
        """Test successful collaboration request."""
        target_agent_id = uuid4()
        response = client.post(
            "/api/v1/openclaw/collaborate",
            json={
                "requester_agent_id": str(test_agent_id),
                "target_agent_id": str(target_agent_id),
                "task": "Research trends on AI ethics",
                "required_capability": "trend_research",
                "input_data": {
                    "topic": "AI ethics",
                    "sources": ["twitter", "news"]
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "status" in data["data"]
        assert data["data"]["status"] in ["accepted", "rejected", "pending"]
        assert "collaboration_id" in data["data"]
    
    def test_request_collaboration_invalid_capability(self, test_agent_id):
        """Test collaboration request with invalid capability."""
        target_agent_id = uuid4()
        response = client.post(
            "/api/v1/openclaw/collaborate",
            json={
                "requester_agent_id": str(test_agent_id),
                "target_agent_id": str(target_agent_id),
                "task": "Test task",
                "required_capability": "invalid_capability"  # Invalid
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_request_collaboration_with_deadline(self, test_agent_id):
        """Test collaboration request with deadline."""
        target_agent_id = uuid4()
        deadline = (datetime.now().replace(microsecond=0)).isoformat()
        response = client.post(
            "/api/v1/openclaw/collaborate",
            json={
                "requester_agent_id": str(test_agent_id),
                "target_agent_id": str(target_agent_id),
                "task": "Research trends",
                "required_capability": "trend_research",
                "deadline": deadline
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_request_collaboration_with_compensation(self, test_agent_id):
        """Test collaboration request with compensation."""
        target_agent_id = uuid4()
        response = client.post(
            "/api/v1/openclaw/collaborate",
            json={
                "requester_agent_id": str(test_agent_id),
                "target_agent_id": str(target_agent_id),
                "task": "Generate content",
                "required_capability": "content_generation",
                "compensation": {
                    "amount": 100.0,
                    "currency": "USD"
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
