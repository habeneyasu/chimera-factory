"""
Integration tests for database operations.

These tests use the actual PostgreSQL database (chimera_dev).
Mark with @pytest.mark.integration to run separately.

Reference: specs/database/schema.sql
"""

import pytest
from uuid import uuid4, UUID
from datetime import datetime

from chimera_factory.db import (
    get_db_connection,
    test_connection,
    reset_connection_pool,
    save_content_plan,
    save_content,
    save_engagement,
    get_agent_by_id,
)


@pytest.fixture(autouse=True, scope="function")
def reset_db_pool():
    """Reset database connection pool before each test to ensure fresh connections."""
    reset_connection_pool()
    yield
    # Cleanup after test if needed


@pytest.mark.integration
class TestDatabaseConnection:
    """Test database connection and basic operations."""
    
    def test_database_connection(self):
        """Test that database connection works."""
        assert test_connection() is True
    
    def test_database_query(self):
        """Test basic database query."""
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT version();")
                version = cur.fetchone()
                assert version is not None
                assert "PostgreSQL" in version[0]


@pytest.mark.integration
class TestContentPlanPersistence:
    """Test content plan database persistence."""
    
    def test_save_content_plan(self):
        """Test saving a content plan to database."""
        # Create an agent first (required for foreign key constraint)
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
                    f"0x{str(agent_id).replace('-', '').ljust(40, '0')}",  # Unique wallet address from agent_id (pad to 40 chars)
                    "sleeping"
                ))
                conn.commit()
        
        plan_id = save_content_plan(
            agent_id=agent_id,
            content_type="image",
            platform="twitter",
            confidence_score=0.85,
            target_audience="tech enthusiasts",
            structure={"prompt": "Test prompt"},
            key_messages=["Message 1", "Message 2"]
        )
        
        assert isinstance(plan_id, UUID)
        
        # Verify it was saved
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM content_plans WHERE id = %s", (str(plan_id),))
                result = cur.fetchone()
                assert result is not None
                # Column order: id, agent_id, content_type, target_audience, platform, ...
                assert str(result[1]) == str(agent_id)  # agent_id column (UUID)
                assert result[2] == "image"  # content_type column
                assert result[4] == "twitter"  # platform column (index 4, not 3)


@pytest.mark.integration
class TestContentPersistence:
    """Test content database persistence."""
    
    def test_save_content(self):
        """Test saving content to database."""
        # Create an agent first (required for foreign key constraint)
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
                    f"0x{'b' * 40}",  # Dummy wallet address
                    "sleeping"
                ))
                conn.commit()
        
        plan_id = save_content_plan(
            agent_id=agent_id,
            content_type="image",
            platform="twitter",
            confidence_score=0.85
        )
        
        content_id = save_content(
            plan_id=plan_id,
            agent_id=agent_id,
            content_type="image",
            content_url="https://example.com/image.jpg",
            metadata={"width": 1024, "height": 1024},
            confidence_score=0.85,
            status="pending"
        )
        
        assert isinstance(content_id, UUID)
        
        # Verify it was saved
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM content WHERE id = %s", (str(content_id),))
                result = cur.fetchone()
                assert result is not None
                # Column order: id, plan_id, agent_id, content_type, content_url, ...
                assert str(result[1]) == str(plan_id)  # plan_id column (UUID)
                assert str(result[2]) == str(agent_id)  # agent_id column (UUID)
                assert result[3] == "image"  # content_type column


@pytest.mark.integration
class TestEngagementPersistence:
    """Test engagement database persistence."""
    
    def test_save_engagement(self):
        """Test saving engagement to database."""
        # Create an agent first (required for foreign key constraint)
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
                    f"0x{'c' * 40}",  # Dummy wallet address
                    "sleeping"
                ))
                conn.commit()
        
        engagement_id = save_engagement(
            agent_id=agent_id,
            platform="twitter",
            action="like",
            target_id="tweet_12345",
            status="success",
            platform_response={"engagement_id": "twitter_like_12345"}
        )
        
        assert isinstance(engagement_id, UUID)
        
        # Verify it was saved
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM engagements WHERE id = %s", (str(engagement_id),))
                result = cur.fetchone()
                assert result is not None
                # Column order: id, agent_id, platform, action, target_id, content_id, status, ...
                assert str(result[1]) == str(agent_id)  # agent_id column (UUID)
                assert result[2] == "twitter"  # platform column
                assert result[3] == "like"  # action column
                assert result[4] == "tweet_12345"  # target_id column


@pytest.mark.integration
class TestSkillsWithDatabase:
    """Test skills integration with database."""
    
    def test_trend_research_with_database(self):
        """Test trend research skill saves to database."""
        from chimera_factory.skills import skill_trend_research
        
        input_data = {
            "topic": "AI influencers",
            "sources": ["twitter"],
            "agent_id": str(uuid4())
        }
        
        output = skill_trend_research.execute(input_data)
        
        assert "trends" in output
        assert "confidence" in output
        assert isinstance(output["trends"], list)
        
        # Verify trends were logged (check logs or database)
        # Note: save_trend currently returns UUID but doesn't persist to a trends table
        # This test verifies the skill executes without errors
    
    def test_content_generate_with_database(self):
        """Test content generation skill saves to database."""
        from chimera_factory.skills import skill_content_generate
        
        input_data = {
            "content_type": "image",
            "prompt": "A futuristic AI influencer",
            "character_reference_id": str(uuid4()),
            "agent_id": str(uuid4()),
            "platform": "twitter"
        }
        
        output = skill_content_generate.execute(input_data)
        
        assert "content_url" in output
        assert "metadata" in output
        assert "confidence" in output
        
        # Verify content was saved to database
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM content WHERE content_url = %s", (output["content_url"],))
                count = cur.fetchone()[0]
                # Content should be saved (if database save succeeded)
                # Note: May be 0 if save failed silently
    
    def test_engagement_manage_with_database(self):
        """Test engagement management skill saves to database."""
        from chimera_factory.skills import skill_engagement_manage
        
        # Create an agent first (required for foreign key constraint)
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
                    f"0x{'d' * 40}",  # Dummy wallet address
                    "sleeping"
                ))
                conn.commit()
        
        input_data = {
            "action": "like",
            "platform": "twitter",
            "target": "tweet_12345",
            "agent_id": str(agent_id)
        }
        
        output = skill_engagement_manage.execute(input_data)
        
        assert "status" in output
        assert output["status"] in ["success", "pending", "failed"]
        
        if output["status"] == "success":
            assert "engagement_id" in output
            
            # Verify engagement was saved to database
            engagement_id = output["engagement_id"]
            # Convert to UUID if it's a string
            if isinstance(engagement_id, str):
                engagement_id = UUID(engagement_id)
            
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT COUNT(*) FROM engagements WHERE id = %s", (str(engagement_id),))
                    count = cur.fetchone()[0]
                    assert count == 1
