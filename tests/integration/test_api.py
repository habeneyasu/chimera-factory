"""
Integration tests for API endpoints.

These tests use TestClient to test the actual API endpoints with real database and skills.

Reference: specs/technical.md (API Contracts)
"""

import pytest
from fastapi.testclient import TestClient
from uuid import uuid4, UUID

from chimera_factory.api import app
from chimera_factory.db import init_database, test_connection, reset_connection_pool, get_db_connection

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


@pytest.fixture(autouse=True, scope="function")
def reset_db_pool():
    """Reset database connection pool before each test."""
    reset_connection_pool()
    yield


@pytest.fixture
def test_agent_id():
    """Create a test agent for foreign key constraints."""
    agent_id = uuid4()
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO agents (id, name, persona_id, wallet_address, status)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                str(agent_id),
                "Test Agent",
                "test_persona",
                f"0x{str(agent_id).replace('-', '').ljust(40, '0')}",
                "sleeping"
            ))
            conn.commit()
    yield agent_id
    # Cleanup
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM agents WHERE id = %s", (str(agent_id),))
            conn.commit()


client = TestClient(app)


@pytest.mark.integration
class TestTrendResearchAPI:
    """Test Trend Research API endpoints."""
    
    def test_research_trends_success(self, test_agent_id):
        """Test successful trend research."""
        response = client.post(
            "/api/v1/trends/research",
            json={
                "topic": "AI influencers",
                "sources": ["twitter"],
                "timeframe": "24h",
                "agent_id": str(test_agent_id)
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "trends" in data["data"]
        assert "confidence" in data["data"]
        assert "request_id" in data["data"]
        
        # Verify trends structure
        trends = data["data"]["trends"]
        assert isinstance(trends, list)
        if trends:
            trend = trends[0]
            assert "title" in trend
            assert "source" in trend
            assert "engagement" in trend
            assert "timestamp" in trend
    
    def test_research_trends_multiple_sources(self, test_agent_id):
        """Test trend research with multiple sources."""
        response = client.post(
            "/api/v1/trends/research",
            json={
                "topic": "artificial intelligence",
                "sources": ["twitter", "news", "reddit"],
                "timeframe": "7d",
                "agent_id": str(test_agent_id)
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "trends" in data["data"]
        assert isinstance(data["data"]["trends"], list)
    
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
    
    def test_research_trends_missing_sources(self):
        """Test trend research with missing sources."""
        response = client.post(
            "/api/v1/trends/research",
            json={
                "topic": "AI influencers",
                "sources": []  # Invalid: empty sources
            }
        )
        
        assert response.status_code == 422  # Validation error


@pytest.mark.integration
class TestContentGenerationAPI:
    """Test Content Generation API endpoints."""
    
    def test_generate_content_text(self, test_agent_id):
        """Test text content generation."""
        response = client.post(
            "/api/v1/content/generate",
            json={
                "content_type": "text",
                "prompt": "Write a tweet about AI influencers",
                "agent_id": str(test_agent_id),
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
        assert 0.0 <= data["data"]["confidence"] <= 1.0
        
        # Verify metadata
        assert "platform" in data["data"]["metadata"]
        assert data["data"]["metadata"]["platform"] == "twitter"
    
    def test_generate_content_image(self, test_agent_id):
        """Test image content generation."""
        character_ref_id = str(uuid4())
        response = client.post(
            "/api/v1/content/generate",
            json={
                "content_type": "image",
                "prompt": "A futuristic AI influencer in a modern setting",
                "character_reference_id": character_ref_id,
                "agent_id": str(test_agent_id),
                "platform": "twitter"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "content_url" in data["data"]
        assert "metadata" in data["data"]
        assert "confidence" in data["data"]
    
    def test_generate_content_with_style(self, test_agent_id):
        """Test content generation with style guide."""
        response = client.post(
            "/api/v1/content/generate",
            json={
                "content_type": "text",
                "prompt": "Create engaging content",
                "style": "modern",
                "agent_id": str(test_agent_id),
                "platform": "twitter"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "content_url" in data["data"]
        assert "confidence" in data["data"]
    
    def test_generate_content_missing_character_ref(self):
        """Test content generation without required character_reference_id for image."""
        response = client.post(
            "/api/v1/content/generate",
            json={
                "content_type": "image",
                "prompt": "A futuristic AI influencer"
            }
        )
        
        # Should succeed but may have lower confidence or use default character
        assert response.status_code in [200, 400, 422]


@pytest.mark.integration
class TestEngagementManagementAPI:
    """Test Engagement Management API endpoints."""
    
    def test_manage_engagement_like(self, test_agent_id):
        """Test successful engagement (like)."""
        response = client.post(
            "/api/v1/engagement/manage",
            json={
                "action": "like",
                "platform": "twitter",
                "target": "tweet_12345",
                "agent_id": str(test_agent_id)
            }
        )
        
        assert response.status_code in [200, 400]  # May fail if API not configured
        data = response.json()
        assert "success" in data
        assert "data" in data
        assert "status" in data["data"]
        assert data["data"]["status"] in ["success", "pending", "failed"]
        
        if data["data"]["status"] == "success":
            assert "engagement_id" in data["data"]
    
    def test_manage_engagement_reply(self, test_agent_id):
        """Test engagement with reply action."""
        response = client.post(
            "/api/v1/engagement/manage",
            json={
                "action": "reply",
                "platform": "twitter",
                "target": "tweet_12345",
                "content": "Great post! Thanks for sharing.",
                "agent_id": str(test_agent_id)
            }
        )
        
        assert response.status_code in [200, 400]
        data = response.json()
        assert "success" in data
        assert "status" in data["data"]
    
    def test_manage_engagement_comment(self, test_agent_id):
        """Test engagement with comment action."""
        response = client.post(
            "/api/v1/engagement/manage",
            json={
                "action": "comment",
                "platform": "instagram",
                "target": "post_12345",
                "content": "Amazing content!",
                "agent_id": str(test_agent_id)
            }
        )
        
        assert response.status_code in [200, 400]
        data = response.json()
        assert "status" in data["data"]
    
    def test_manage_engagement_multiple_platforms(self, test_agent_id):
        """Test engagement on different platforms."""
        platforms = ["twitter", "instagram", "tiktok"]
        
        for platform in platforms:
            response = client.post(
                "/api/v1/engagement/manage",
                json={
                    "action": "like",
                    "platform": platform,
                    "target": f"{platform}_post_123",
                    "agent_id": str(test_agent_id)
                }
            )
            
            assert response.status_code in [200, 400]
            data = response.json()
            assert "status" in data["data"]
    
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
        
        # Should return failed status or validation error
        assert response.status_code in [200, 400, 422]
        data = response.json()
        if not data.get("success"):
            assert "error" in data.get("data", {}) or "error" in data


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
        
        # Verify agent structure if agents exist
        if data["data"]:
            agent = data["data"][0]
            assert "id" in agent
            assert "name" in agent
            assert "persona_id" in agent
            assert "wallet_address" in agent
            assert "status" in agent
    
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
        assert "persona_id" in data["data"]
        assert "wallet_address" in data["data"]
        assert "status" in data["data"]
        assert data["data"]["status"] == "sleeping"
    
    def test_create_agent_with_wallet(self):
        """Test creating an agent with custom wallet address."""
        wallet = "0x1234567890123456789012345678901234567890"
        response = client.post(
            "/api/v1/agents",
            json={
                "name": "Agent With Wallet",
                "persona_id": "test_persona_002",
                "wallet_address": wallet
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["wallet_address"] == wallet
    
    def test_get_agent_by_id_success(self, test_agent_id):
        """Test getting an agent by ID (success case)."""
        response = client.get(f"/api/v1/agents/{test_agent_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert data["data"]["id"] == str(test_agent_id)
        assert data["data"]["name"] == "Test Agent"
        assert "persona_id" in data["data"]
        assert "wallet_address" in data["data"]
        assert "status" in data["data"]
    
    def test_get_agent_not_found(self):
        """Test getting non-existent agent."""
        fake_id = uuid4()
        response = client.get(f"/api/v1/agents/{fake_id}")
        
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "NOT_FOUND"
        assert f"Agent {fake_id}" in data["error"]["message"]
    
    def test_list_agents_includes_created(self):
        """Test that created agents appear in list."""
        # Create an agent
        create_response = client.post(
            "/api/v1/agents",
            json={
                "name": "List Test Agent",
                "persona_id": "test_persona_list"
            }
        )
        created_agent_id = create_response.json()["data"]["id"]
        
        # List agents
        list_response = client.get("/api/v1/agents")
        assert list_response.status_code == 200
        agents = list_response.json()["data"]
        
        # Verify created agent is in the list
        agent_ids = [agent["id"] for agent in agents]
        assert created_agent_id in agent_ids


@pytest.mark.integration
class TestCampaignAPI:
    """Test Campaign API endpoints."""
    
    def test_create_campaign(self, test_agent_id):
        """Test creating a new campaign with existing agent."""
        response = client.post(
            "/api/v1/campaigns",
            json={
                "goal": "Increase engagement on AI topics",
                "agent_ids": [str(test_agent_id)]
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert data["data"]["goal"] == "Increase engagement on AI topics"
        assert str(test_agent_id) in data["data"]["agent_ids"]
        assert "id" in data["data"]
        assert "status" in data["data"]
        assert data["data"]["status"] == "active"
        assert "created_at" in data["data"]
    
    def test_create_campaign_multiple_agents(self):
        """Test creating a campaign with multiple agents."""
        # Create multiple agents
        agent_ids = []
        for i in range(2):
            agent_response = client.post(
                "/api/v1/agents",
                json={
                    "name": f"Campaign Agent {i+1}",
                    "persona_id": f"test_persona_campaign_{i+1}"
                }
            )
            agent_ids.append(agent_response.json()["data"]["id"])
        
        # Create campaign with multiple agents
        response = client.post(
            "/api/v1/campaigns",
            json={
                "goal": "Multi-agent campaign test",
                "agent_ids": agent_ids
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["agent_ids"]) == 2
        assert all(agent_id in data["data"]["agent_ids"] for agent_id in agent_ids)
    
    def test_create_campaign_validation_error(self):
        """Test campaign creation with invalid input."""
        # Missing goal
        response = client.post(
            "/api/v1/campaigns",
            json={
                "agent_ids": [str(uuid4())]
            }
        )
        assert response.status_code == 422  # Validation error
        
        # Empty agent_ids
        response = client.post(
            "/api/v1/campaigns",
            json={
                "goal": "Test goal",
                "agent_ids": []
            }
        )
        assert response.status_code == 422  # Validation error


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
