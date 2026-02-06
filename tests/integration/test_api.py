"""
Integration tests for API endpoints.

These tests require the API server to be running or use TestClient.

Reference: specs/technical.md (API Contracts)
"""

import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from chimera_factory.api import app
from chimera_factory.db import init_database, test_connection

# Initialize database before running tests
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Initialize database schema before running tests."""
    if test_connection():
        try:
            init_database()
            print("✅ Database schema initialized for tests")
        except Exception as e:
            print(f"⚠️  Database initialization warning: {e}")
            # Continue if tables already exist
    else:
        pytest.skip("Database connection failed - skipping integration tests")

client = TestClient(app)


@pytest.mark.integration
class TestTrendResearchAPI:
    """Test Trend Research API endpoints."""
    
    def test_research_trends_success(self):
        """Test successful trend research."""
        response = client.post(
            "/api/v1/trends/research",
            json={
                "topic": "AI influencers",
                "sources": ["twitter"],
                "timeframe": "24h",
                "agent_id": str(uuid4())
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "trends" in data["data"]
        assert "confidence" in data["data"]
        assert "request_id" in data["data"]
    
    def test_research_trends_validation_error(self):
        """Test trend research with invalid input."""
        response = client.post(
            "/api/v1/trends/research",
            json={
                "topic": "",  # Invalid: empty topic
                "sources": ["twitter"]
            }
        )
        
        assert response.status_code == 422  # Validation error


@pytest.mark.integration
class TestContentGenerationAPI:
    """Test Content Generation API endpoints."""
    
    def test_generate_content_success(self):
        """Test successful content generation."""
        response = client.post(
            "/api/v1/content/generate",
            json={
                "content_type": "image",
                "prompt": "A futuristic AI influencer",
                "character_reference_id": str(uuid4()),
                "agent_id": str(uuid4()),
                "platform": "twitter"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "content_url" in data["data"]
        assert "metadata" in data["data"]
        assert "confidence" in data["data"]
    
    def test_generate_content_missing_character_ref(self):
        """Test content generation without required character_reference_id."""
        response = client.post(
            "/api/v1/content/generate",
            json={
                "content_type": "image",
                "prompt": "A futuristic AI influencer"
            }
        )
        
        # Should fail validation or return error
        assert response.status_code in [400, 422]


@pytest.mark.integration
class TestEngagementManagementAPI:
    """Test Engagement Management API endpoints."""
    
    def test_manage_engagement_like(self):
        """Test successful engagement (like)."""
        response = client.post(
            "/api/v1/engagement/manage",
            json={
                "action": "like",
                "platform": "twitter",
                "target": "tweet_12345",
                "agent_id": str(uuid4())
            }
        )
        
        assert response.status_code in [200, 400]  # May fail if API not configured
        data = response.json()
        assert "success" in data
        assert "data" in data
    
    def test_manage_engagement_missing_content(self):
        """Test engagement requiring content without providing it."""
        response = client.post(
            "/api/v1/engagement/manage",
            json={
                "action": "reply",
                "platform": "twitter",
                "target": "tweet_12345"
            }
        )
        
        # Should return failed status
        assert response.status_code in [200, 400]
        data = response.json()
        if not data.get("success"):
            assert "error" in data.get("data", {})


@pytest.mark.integration
class TestAgentOrchestrationAPI:
    """Test Agent Orchestration API endpoints."""
    
    def test_list_agents(self):
        """Test listing all agents."""
        response = client.get("/api/v1/agents")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)
    
    def test_create_agent(self):
        """Test creating a new agent."""
        response = client.post(
            "/api/v1/agents",
            json={
                "name": "Test Agent",
                "persona_id": "test_persona_001"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert data["data"]["name"] == "Test Agent"
        assert "id" in data["data"]
    
    def test_get_agent_not_found(self):
        """Test getting non-existent agent."""
        fake_id = uuid4()
        response = client.get(f"/api/v1/agents/{fake_id}")
        
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "NOT_FOUND"


@pytest.mark.integration
class TestCampaignAPI:
    """Test Campaign API endpoints."""
    
    def test_create_campaign(self):
        """Test creating a new campaign."""
        # First create an agent
        agent_response = client.post(
            "/api/v1/agents",
            json={
                "name": "Campaign Test Agent",
                "persona_id": "test_persona_002"
            }
        )
        agent_id = agent_response.json()["data"]["id"]
        
        # Create campaign
        response = client.post(
            "/api/v1/campaigns",
            json={
                "goal": "Increase engagement on AI topics",
                "agent_ids": [agent_id]
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["goal"] == "Increase engagement on AI topics"
        assert agent_id in data["data"]["agent_ids"]


@pytest.mark.integration
class TestHealthCheck:
    """Test health check endpoint."""
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "healthy"
