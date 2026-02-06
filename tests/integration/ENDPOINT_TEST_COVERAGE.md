# API Endpoint Test Coverage

This document summarizes all API endpoint tests in `test_api.py`.

## Test Coverage Summary

### ✅ Trends API
**Endpoint**: `POST /api/v1/trends/research`

- ✅ `test_research_trends_success` - Basic trend research with agent_id
- ✅ `test_research_trends_multiple_sources` - Multiple sources (Twitter, News, Reddit)
- ✅ `test_research_trends_validation_error` - Invalid input (empty topic)
- ✅ `test_research_trends_missing_sources` - Empty sources validation

### ✅ Content Generation API
**Endpoint**: `POST /api/v1/content/generate`

- ✅ `test_generate_content_text` - Text content generation
- ✅ `test_generate_content_image` - Image content with character reference
- ✅ `test_generate_content_with_style` - Style guide integration
- ✅ `test_generate_content_missing_character_ref` - Validation for image without character_ref

### ✅ Engagement Management API
**Endpoint**: `POST /api/v1/engagement/manage`

- ✅ `test_manage_engagement_like` - Like action
- ✅ `test_manage_engagement_reply` - Reply with content
- ✅ `test_manage_engagement_comment` - Comment action
- ✅ `test_manage_engagement_multiple_platforms` - Twitter, Instagram, TikTok
- ✅ `test_manage_engagement_missing_content` - Validation for reply without content

### ✅ Agent Orchestration API

#### `GET /api/v1/agents` - List Agents
- ✅ `test_list_agents` - List all agents with structure validation

#### `POST /api/v1/agents` - Create Agent
- ✅ `test_create_agent` - Create agent with basic fields
- ✅ `test_create_agent_with_wallet` - Create agent with custom wallet address

#### `GET /api/v1/agents/{agent_id}` - Get Agent
- ✅ `test_get_agent_by_id_success` - Get existing agent by ID
- ✅ `test_get_agent_not_found` - Get non-existent agent (404)
- ✅ `test_list_agents_includes_created` - Verify created agents appear in list

### ✅ Campaign API
**Endpoint**: `POST /api/v1/campaigns`

- ✅ `test_create_campaign` - Create campaign with existing agent
- ✅ `test_create_campaign_multiple_agents` - Create campaign with multiple agents
- ✅ `test_create_campaign_validation_error` - Validation errors (missing goal, empty agent_ids)

### ✅ Health Check
**Endpoint**: `GET /api/v1/health`

- ✅ `test_health_check` - Health check endpoint

## Running Tests

```bash
# Run all API endpoint tests
make test

# Run specific endpoint tests
uv run pytest tests/integration/test_api.py::TestTrendResearchAPI -v
uv run pytest tests/integration/test_api.py::TestContentGenerationAPI -v
uv run pytest tests/integration/test_api.py::TestEngagementManagementAPI -v
uv run pytest tests/integration/test_api.py::TestAgentOrchestrationAPI -v
uv run pytest tests/integration/test_api.py::TestCampaignAPI -v

# Run all endpoint tests
uv run pytest tests/integration/test_api.py -v
```

## Test Features

- ✅ Uses `test_agent_id` fixture for foreign key constraints
- ✅ Database persistence verification
- ✅ Response structure validation
- ✅ Error handling and validation testing
- ✅ Multiple platforms and content types
- ✅ Edge cases and error scenarios
