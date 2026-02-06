# Chimera Orchestrator API Documentation

**Version**: 0.1.0  
**Base URL**: Configured via `.env` file (default: `http://localhost:8000/api/v1`)  
**Reference**: `specs/technical.md`, `specs/api/orchestrator.yaml`

## Configuration

All sensitive configuration is stored in the `.env` file. Copy `.env.example` to `.env` and update with your values:

```bash
cp .env.example .env
# Edit .env with your actual configuration
```

Key configuration variables:
- `API_HOST`: Server host (default: `0.0.0.0`)
- `API_PORT`: Server port (default: `8000`)
- `API_RELOAD`: Enable auto-reload (default: `true`)
- `CORS_ORIGINS`: Allowed CORS origins (default: `*`)
- `POSTGRES_*`: Database configuration
- `REDIS_*`: Redis configuration
- External API keys for Twitter, News, Reddit, Ideogram, Runway, etc.

## Quick Start

### Start the API Server

```bash
# Using Makefile (reads from .env)
make run-api

# Or directly (reads from .env)
uv run python scripts/run_api.py

# Or override environment variables
API_PORT=8080 uv run python scripts/run_api.py
```

### Access API Documentation

The base URL is configured via `API_HOST` and `API_PORT` in `.env` (default: `http://localhost:8000`):

- **Swagger UI**: `http://<API_HOST>:<API_PORT>/api/v1/docs`
- **ReDoc**: `http://<API_HOST>:<API_PORT>/api/v1/redoc`
- **OpenAPI JSON**: `http://<API_HOST>:<API_PORT>/api/v1/openapi.json`

## Endpoints

### Health Check

**GET** `/api/v1/health`

Check API health status.

**Response**:
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "version": "0.1.0"
  },
  "error": null,
  "timestamp": "2026-02-04T12:00:00Z"
}
```

### Trend Research API

**POST** `/api/v1/trends/research`

Research trends from multiple sources (Twitter, News, Reddit, etc.).

**Request Body**:
```json
{
  "topic": "AI influencers",
  "sources": ["twitter", "news"],
  "timeframe": "24h",
  "agent_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "trends": [
      {
        "id": "uuid",
        "title": "Trending: AI influencers",
        "source": "twitter",
        "engagement": 5000,
        "timestamp": "2026-02-04T12:00:00Z",
        "url": "https://twitter.com/...",
        "relevance_score": 0.85
      }
    ],
    "confidence": 0.8,
    "request_id": "uuid"
  },
  "error": null,
  "timestamp": "2026-02-04T12:00:00Z"
}
```

### Content Generation API

**POST** `/api/v1/content/generate`

Generate multimodal content (text, image, video).

**Request Body**:
```json
{
  "content_type": "image",
  "prompt": "A futuristic AI influencer",
  "style": "modern",
  "character_reference_id": "123e4567-e89b-12d3-a456-426614174000",
  "agent_id": "123e4567-e89b-12d3-a456-426614174000",
  "platform": "twitter"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "content_url": "https://example.com/content/12345",
    "metadata": {
      "platform": "twitter",
      "format": "image",
      "dimensions": {"width": 1024, "height": 1024}
    },
    "confidence": 0.85
  },
  "error": null,
  "timestamp": "2026-02-04T12:00:00Z"
}
```

### Engagement Management API

**POST** `/api/v1/engagement/manage`

Manage social media engagement actions (reply, like, follow, comment, share).

**Request Body**:
```json
{
  "action": "like",
  "platform": "twitter",
  "target": "tweet_12345",
  "agent_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "status": "success",
    "engagement_id": "uuid",
    "platform_response": {
      "engagement_id": "twitter_like_12345"
    }
  },
  "error": null,
  "timestamp": "2026-02-04T12:00:00Z"
}
```

### Agent Orchestration API

#### List Agents

**GET** `/api/v1/agents`

List all agents.

**Response** (200 OK):
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "name": "Agent Name",
      "status": "sleeping",
      "wallet_address": "0x...",
      "persona_id": "persona_001",
      "created_at": "2026-02-04T12:00:00Z"
    }
  ],
  "error": null,
  "timestamp": "2026-02-04T12:00:00Z"
}
```

#### Create Agent

**POST** `/api/v1/agents`

Create a new agent.

**Request Body**:
```json
{
  "name": "Agent Name",
  "persona_id": "persona_001",
  "wallet_address": "0x..." // optional
}
```

**Response** (201 Created):
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "Agent Name",
    "status": "sleeping",
    "wallet_address": "0x...",
    "persona_id": "persona_001",
    "created_at": "2026-02-04T12:00:00Z"
  },
  "error": null,
  "timestamp": "2026-02-04T12:00:00Z"
}
```

#### Get Agent

**GET** `/api/v1/agents/{agent_id}`

Get agent details by ID.

**Response** (200 OK): Same as create agent response.

### Campaign API

#### Create Campaign

**POST** `/api/v1/campaigns`

Create a new campaign.

**Request Body**:
```json
{
  "goal": "Increase engagement on AI topics",
  "agent_ids": ["uuid1", "uuid2"]
}
```

**Response** (201 Created):
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "goal": "Increase engagement on AI topics",
    "status": "active",
    "agent_ids": ["uuid1", "uuid2"],
    "created_at": "2026-02-04T12:00:00Z"
  },
  "error": null,
  "timestamp": "2026-02-04T12:00:00Z"
}
```

## Error Responses

All errors follow this format:

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {}
  },
  "timestamp": "2026-02-04T12:00:00Z"
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid request parameters |
| `NOT_FOUND` | 404 | Resource not found |
| `RATE_LIMIT_EXCEEDED` | 429 | Rate limit exceeded |
| `TREND_RESEARCH_ERROR` | 500 | Trend research failed |
| `CONTENT_GENERATION_ERROR` | 500 | Content generation failed |
| `ENGAGEMENT_ERROR` | 500 | Engagement management failed |
| `INTERNAL_ERROR` | 500 | Internal server error |

## Testing

Run API integration tests:

```bash
# Run all API tests
uv run pytest tests/integration/test_api.py -v

# Run specific test
uv run pytest tests/integration/test_api.py::TestTrendResearchAPI::test_research_trends_success -v
```

## Implementation Details

- **Framework**: FastAPI
- **Validation**: Pydantic v2 models
- **Database**: PostgreSQL (via connection pool)
- **Caching**: Redis (for performance)
- **Rate Limiting**: Platform-specific limits
- **Logging**: Structured logging with audit trails
- **Error Handling**: Custom exception hierarchy

## References

- **Technical Specs**: `specs/technical.md`
- **OpenAPI Spec**: `specs/api/orchestrator.yaml`
- **Database Schema**: `specs/database/schema.sql`
- **Skill Contracts**: `skills/*/contract.json`
