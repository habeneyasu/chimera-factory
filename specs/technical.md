# Technical Specifications: Project Chimera

**Prepared By**: habeneyasu  
**Repository**: [https://github.com/habeneyasu/chimera-factory](https://github.com/habeneyasu/chimera-factory)  
**Last Updated**: February 2026  
**Version**: 1.0.0

---

## Overview

This document defines the technical architecture, API contracts, and system interfaces for Project Chimera. All API contracts use JSON Schema for machine-readable validation.

**Reference**: See `specs/_meta.md` for architectural constraints and `specs/functional.md` for user stories.

---

## API Architecture

### Base URL

All APIs follow RESTful conventions and are versioned:

```
http://localhost:8000/api/v1
```

### Authentication

All API requests require authentication via API key or JWT token:

```
Authorization: Bearer <token>
```

### Response Format

All API responses follow this structure:

```json
{
  "success": true,
  "data": { ... },
  "error": null,
  "timestamp": "2026-02-04T12:00:00Z"
}
```

Error responses:

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": { ... }
  },
  "timestamp": "2026-02-04T12:00:00Z"
}
```

---

## API Contracts

### 1. Trend Research API

#### POST /api/v1/trends/research

Research trends from multiple sources.

**Request Body**:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "topic": {
      "type": "string",
      "description": "Topic or keyword to research",
      "minLength": 1,
      "maxLength": 255
    },
    "sources": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": ["twitter", "youtube", "news", "reddit", "openclaw"]
      },
      "description": "List of sources to query",
      "minItems": 1,
      "maxItems": 10
    },
    "timeframe": {
      "type": "string",
      "enum": ["1h", "24h", "7d", "30d"],
      "default": "24h",
      "description": "Time window for trend analysis"
    },
    "filters": {
      "type": "object",
      "properties": {
        "min_engagement": {
          "type": "number",
          "minimum": 0,
          "description": "Minimum engagement score"
        },
        "min_relevance": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "Minimum relevance score"
        }
      }
    },
    "agent_id": {
      "type": "string",
      "format": "uuid",
      "description": "ID of the agent making the request"
    }
  },
  "required": ["topic", "sources", "agent_id"]
}
```

**Response Body** (200 OK):

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "trends": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": {
            "type": "string",
            "format": "uuid"
          },
          "title": {
            "type": "string"
          },
          "source": {
            "type": "string",
            "enum": ["twitter", "youtube", "news", "reddit", "openclaw"]
          },
          "url": {
            "type": "string",
            "format": "uri"
          },
          "engagement": {
            "type": "number",
            "minimum": 0,
            "description": "Engagement metric (likes, views, etc.)"
          },
          "relevance_score": {
            "type": "number",
            "minimum": 0,
            "maximum": 1
          },
          "velocity": {
            "type": "number",
            "description": "Rate of growth (trend velocity)"
          },
          "hashtags": {
            "type": "array",
            "items": {
              "type": "string"
            }
          },
          "related_topics": {
            "type": "array",
            "items": {
              "type": "string"
            }
          },
          "timestamp": {
            "type": "string",
            "format": "date-time"
          },
          "attribution": {
            "type": "object",
            "properties": {
              "agent_id": {
                "type": "string",
                "format": "uuid"
              },
              "agent_name": {
                "type": "string"
              }
            },
            "description": "Attribution for OpenClaw-sourced trends"
          }
        },
        "required": ["id", "title", "source", "engagement", "timestamp"]
      }
    },
    "analysis": {
      "type": "object",
      "properties": {
        "total_trends": {
          "type": "integer",
          "minimum": 0
        },
        "top_trend": {
          "type": "string",
          "format": "uuid"
        },
        "confidence": {
          "type": "number",
          "minimum": 0,
          "maximum": 1
        },
        "trend_velocity": {
          "type": "number"
        }
      },
      "required": ["total_trends", "confidence"]
    },
    "request_id": {
      "type": "string",
      "format": "uuid"
    }
  },
  "required": ["trends", "analysis", "request_id"]
}
```

**Error Responses**:
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Missing or invalid authentication
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

---

### 2. Content Planning API

#### POST /api/v1/content/plans

Create a content plan from trend research results.

**Request Body**:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "agent_id": {
      "type": "string",
      "format": "uuid",
      "description": "ID of the agent creating the plan"
    },
    "trend_ids": {
      "type": "array",
      "items": {
        "type": "string",
        "format": "uuid"
      },
      "description": "IDs of trends to base content on",
      "minItems": 1
    },
    "content_type": {
      "type": "string",
      "enum": ["text", "image", "video", "multimodal"],
      "description": "Type of content to generate"
    },
    "target_audience": {
      "type": "string",
      "description": "Target audience description"
    },
    "key_messages": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "Key messages to convey",
      "minItems": 1
    },
    "platform": {
      "type": "string",
      "enum": ["twitter", "instagram", "tiktok", "youtube", "threads"],
      "description": "Target platform for content"
    },
    "style_guidelines": {
      "type": "object",
      "properties": {
        "tone": {
          "type": "string",
          "enum": ["professional", "casual", "humorous", "serious", "inspirational"]
        },
        "voice": {
          "type": "string",
          "description": "Brand voice description"
        }
      }
    }
  },
  "required": ["agent_id", "trend_ids", "content_type", "platform"]
}
```

**Response Body** (200 OK):

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "plan_id": {
      "type": "string",
      "format": "uuid"
    },
    "agent_id": {
      "type": "string",
      "format": "uuid"
    },
    "content_type": {
      "type": "string",
      "enum": ["text", "image", "video", "multimodal"]
    },
    "structure": {
      "type": "object",
      "properties": {
        "title": {
          "type": "string"
        },
        "sections": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "type": {
                "type": "string"
              },
              "content": {
                "type": "string"
              }
            }
          }
        }
      }
    },
    "target_audience": {
      "type": "string"
    },
    "key_messages": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "platform": {
      "type": "string"
    },
    "confidence_score": {
      "type": "number",
      "minimum": 0,
      "maximum": 1
    },
    "approval_status": {
      "type": "string",
      "enum": ["auto_approved", "pending", "rejected"],
      "description": "Auto-approved if confidence > 0.90, pending if 0.70-0.90, rejected if < 0.70"
    },
    "trend_references": {
      "type": "array",
      "items": {
        "type": "string",
        "format": "uuid"
      }
    },
    "created_at": {
      "type": "string",
      "format": "date-time"
    }
  },
  "required": ["plan_id", "agent_id", "content_type", "confidence_score", "approval_status", "created_at"]
}
```

---

### 3. Content Generation API

#### POST /api/v1/content/generate

Generate content from an approved content plan.

**Request Body**:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "plan_id": {
      "type": "string",
      "format": "uuid",
      "description": "ID of the approved content plan"
    },
    "agent_id": {
      "type": "string",
      "format": "uuid"
    },
    "variations": {
      "type": "integer",
      "minimum": 1,
      "maximum": 5,
      "default": 1,
      "description": "Number of content variations to generate"
    },
    "options": {
      "type": "object",
      "properties": {
        "include_hashtags": {
          "type": "boolean",
          "default": true
        },
        "include_mentions": {
          "type": "boolean",
          "default": false
        },
        "character_reference_id": {
          "type": "string",
          "description": "Character consistency lock ID for visual content"
        }
      }
    }
  },
  "required": ["plan_id", "agent_id"]
}
```

**Response Body** (200 OK):

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "content_items": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "content_id": {
            "type": "string",
            "format": "uuid"
          },
          "plan_id": {
            "type": "string",
            "format": "uuid"
          },
          "agent_id": {
            "type": "string",
            "format": "uuid"
          },
          "content_type": {
            "type": "string",
            "enum": ["text", "image", "video", "multimodal"]
          },
          "content_url": {
            "type": "string",
            "format": "uri",
            "description": "URL or path to generated content"
          },
          "metadata": {
            "type": "object",
            "properties": {
              "platform": {
                "type": "string"
              },
              "format": {
                "type": "string"
              },
              "dimensions": {
                "type": "object",
                "properties": {
                  "width": {
                    "type": "integer"
                  },
                  "height": {
                    "type": "integer"
                  }
                }
              },
              "duration": {
                "type": "number",
                "description": "Duration in seconds (for video)"
              },
              "file_size": {
                "type": "integer",
                "description": "File size in bytes"
              },
              "hashtags": {
                "type": "array",
                "items": {
                  "type": "string"
                }
              }
            }
          },
          "confidence_score": {
            "type": "number",
            "minimum": 0,
            "maximum": 1
          },
          "approval_status": {
            "type": "string",
            "enum": ["auto_approved", "pending", "rejected"]
          },
          "created_at": {
            "type": "string",
            "format": "date-time"
          }
        },
        "required": ["content_id", "content_type", "content_url", "confidence_score", "approval_status", "created_at"]
      }
    },
    "generation_metadata": {
      "type": "object",
      "properties": {
        "total_variations": {
          "type": "integer"
        },
        "generation_time_ms": {
          "type": "integer"
        },
        "model_used": {
          "type": "string"
        }
      }
    }
  },
  "required": ["content_items"]
}
```

---

### 4. Approval Workflow API

#### POST /api/v1/approvals/request

Submit content for human approval.

**Request Body**:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "content_id": {
      "type": "string",
      "format": "uuid",
      "description": "ID of content or plan to approve"
    },
    "approval_type": {
      "type": "string",
      "enum": ["plan", "content"],
      "description": "Type of item to approve"
    },
    "priority": {
      "type": "string",
      "enum": ["low", "medium", "high", "urgent"],
      "default": "medium"
    },
    "timeout_hours": {
      "type": "integer",
      "minimum": 1,
      "maximum": 168,
      "default": 24,
      "description": "Hours before auto-approval (if enabled)"
    }
  },
  "required": ["content_id", "approval_type"]
}
```

**Response Body** (200 OK):

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "approval_id": {
      "type": "string",
      "format": "uuid"
    },
    "content_id": {
      "type": "string",
      "format": "uuid"
    },
    "approval_type": {
      "type": "string",
      "enum": ["plan", "content"]
    },
    "status": {
      "type": "string",
      "enum": ["pending", "approved", "rejected", "auto_approved"]
    },
    "priority": {
      "type": "string"
    },
    "submitted_at": {
      "type": "string",
      "format": "date-time"
    },
    "expires_at": {
      "type": "string",
      "format": "date-time",
      "description": "Auto-approval deadline"
    }
  },
  "required": ["approval_id", "content_id", "approval_type", "status", "submitted_at"]
}
```

#### POST /api/v1/approvals/{approval_id}/respond

Respond to an approval request (human action).

**Request Body**:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "decision": {
      "type": "string",
      "enum": ["approve", "reject"]
    },
    "feedback": {
      "type": "string",
      "description": "Optional feedback for the agent"
    },
    "modifications": {
      "type": "object",
      "description": "Optional modifications to request"
    }
  },
  "required": ["decision"]
}
```

**Response Body** (200 OK):

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "approval_id": {
      "type": "string",
      "format": "uuid"
    },
    "status": {
      "type": "string",
      "enum": ["approved", "rejected"]
    },
    "decision": {
      "type": "string"
    },
    "feedback": {
      "type": "string"
    },
    "decided_at": {
      "type": "string",
      "format": "date-time"
    },
    "decided_by": {
      "type": "string",
      "description": "User ID who made the decision"
    }
  },
  "required": ["approval_id", "status", "decision", "decided_at"]
}
```

---

### 5. Engagement Management API

#### GET /api/v1/engagement/monitor

Monitor engagement metrics for published content.

**Query Parameters**:
- `agent_id` (required): UUID of the agent
- `platform` (optional): Filter by platform
- `start_date` (optional): ISO 8601 date
- `end_date` (optional): ISO 8601 date

**Response Body** (200 OK):

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "engagements": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "engagement_id": {
            "type": "string",
            "format": "uuid"
          },
          "content_id": {
            "type": "string",
            "format": "uuid"
          },
          "platform": {
            "type": "string"
          },
          "type": {
            "type": "string",
            "enum": ["like", "comment", "share", "follow", "view"]
          },
          "count": {
            "type": "integer",
            "minimum": 0
          },
          "timestamp": {
            "type": "string",
            "format": "date-time"
          },
          "priority": {
            "type": "string",
            "enum": ["low", "medium", "high"],
            "description": "Priority for response"
          }
        },
        "required": ["engagement_id", "content_id", "platform", "type", "count", "timestamp"]
      }
    },
    "summary": {
      "type": "object",
      "properties": {
        "total_engagements": {
          "type": "integer"
        },
        "high_priority_count": {
          "type": "integer"
        },
        "platforms": {
          "type": "object",
          "additionalProperties": {
            "type": "integer"
          }
        }
      }
    }
  },
  "required": ["engagements", "summary"]
}
```

#### POST /api/v1/engagement/respond

Respond to an engagement (comment, message, etc.).

**Request Body**:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "agent_id": {
      "type": "string",
      "format": "uuid"
    },
    "engagement_id": {
      "type": "string",
      "format": "uuid",
      "description": "ID of engagement to respond to"
    },
    "action": {
      "type": "string",
      "enum": ["reply", "like", "follow", "comment", "share"]
    },
    "content": {
      "type": "string",
      "description": "Response content (for reply/comment)",
      "maxLength": 5000
    },
    "requires_approval": {
      "type": "boolean",
      "default": false,
      "description": "Whether response requires human approval"
    }
  },
  "required": ["agent_id", "engagement_id", "action"]
}
```

**Response Body** (200 OK):

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "response_id": {
      "type": "string",
      "format": "uuid"
    },
    "engagement_id": {
      "type": "string",
      "format": "uuid"
    },
    "status": {
      "type": "string",
      "enum": ["success", "pending", "failed", "requires_approval"]
    },
    "platform_response": {
      "type": "object",
      "description": "Raw response from platform API"
    },
    "created_at": {
      "type": "string",
      "format": "date-time"
    }
  },
  "required": ["response_id", "engagement_id", "status", "created_at"]
}
```

---

### 6. OpenClaw Integration API

#### POST /api/v1/openclaw/publish

Publish agent capabilities and status to OpenClaw network.

**Request Body**:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "agent_id": {
      "type": "string",
      "format": "uuid"
    },
    "capabilities": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": ["trend_research", "content_generation", "engagement_management"]
      },
      "description": "Available skills"
    },
    "status": {
      "type": "string",
      "enum": ["idle", "researching", "generating", "engaging", "sleeping"]
    },
    "resources": {
      "type": "object",
      "properties": {
        "cpu_usage": {
          "type": "number",
          "minimum": 0,
          "maximum": 100
        },
        "memory_usage": {
          "type": "number",
          "minimum": 0,
          "maximum": 100
        },
        "queue_depth": {
          "type": "integer",
          "minimum": 0
        }
      }
    }
  },
  "required": ["agent_id", "capabilities", "status"]
}
```

**Response Body** (200 OK):

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "publication_id": {
      "type": "string",
      "format": "uuid"
    },
    "agent_id": {
      "type": "string",
      "format": "uuid"
    },
    "published_at": {
      "type": "string",
      "format": "date-time"
    },
    "network_reachable": {
      "type": "boolean"
    }
  },
  "required": ["publication_id", "agent_id", "published_at", "network_reachable"]
}
```

#### POST /api/v1/openclaw/discover

Discover other agents in the OpenClaw network.

**Request Body**:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "capabilities": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "Required capabilities"
    },
    "status": {
      "type": "string",
      "enum": ["idle", "available"],
      "description": "Filter by agent status"
    },
    "min_reputation": {
      "type": "number",
      "minimum": 0,
      "maximum": 1
    },
    "limit": {
      "type": "integer",
      "minimum": 1,
      "maximum": 100,
      "default": 10
    }
  }
}
```

**Response Body** (200 OK):

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "agents": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "agent_id": {
            "type": "string",
            "format": "uuid"
          },
          "name": {
            "type": "string"
          },
          "capabilities": {
            "type": "array",
            "items": {
              "type": "string"
            }
          },
          "status": {
            "type": "string"
          },
          "reputation": {
            "type": "number",
            "minimum": 0,
            "maximum": 1
          },
          "resources": {
            "type": "object",
            "properties": {
              "cpu_usage": {
                "type": "number"
              },
              "memory_usage": {
                "type": "number"
              },
              "queue_depth": {
                "type": "integer"
              }
            }
          }
        },
        "required": ["agent_id", "name", "capabilities", "status"]
      }
    },
    "total_found": {
      "type": "integer"
    }
  },
  "required": ["agents", "total_found"]
}
```

#### POST /api/v1/openclaw/collaborate

Request collaboration with another agent.

**Request Body**:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "requester_agent_id": {
      "type": "string",
      "format": "uuid"
    },
    "target_agent_id": {
      "type": "string",
      "format": "uuid"
    },
    "task": {
      "type": "string",
      "description": "Task description"
    },
    "required_capability": {
      "type": "string",
      "description": "Required capability"
    },
    "deadline": {
      "type": "string",
      "format": "date-time"
    }
  },
  "required": ["requester_agent_id", "target_agent_id", "task", "required_capability"]
}
```

**Response Body** (200 OK):

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "collaboration_id": {
      "type": "string",
      "format": "uuid"
    },
    "status": {
      "type": "string",
      "enum": ["pending", "accepted", "rejected"]
    },
    "response": {
      "type": "object",
      "description": "Response from target agent"
    },
    "created_at": {
      "type": "string",
      "format": "date-time"
    }
  },
  "required": ["collaboration_id", "status", "created_at"]
}
```

---

### 7. Agent Orchestration API

See `specs/api/orchestrator.yaml` for detailed OpenAPI specification.

**Key Endpoints**:
- `GET /api/v1/agents`: List all agents
- `POST /api/v1/agents`: Create a new agent
- `GET /api/v1/agents/{agent_id}`: Get agent details
- `POST /api/v1/campaigns`: Create a new campaign
- `GET /api/v1/tasks`: List tasks
- `POST /api/v1/tasks`: Create a task

---

## Data Models

### Trend

```json
{
  "id": "uuid",
  "title": "string",
  "source": "string",
  "url": "uri",
  "engagement": "number",
  "relevance_score": "number (0-1)",
  "velocity": "number",
  "hashtags": ["string"],
  "related_topics": ["string"],
  "timestamp": "datetime",
  "attribution": {
    "agent_id": "uuid",
    "agent_name": "string"
  }
}
```

### Content Plan

```json
{
  "plan_id": "uuid",
  "agent_id": "uuid",
  "content_type": "text|image|video|multimodal",
  "structure": {
    "title": "string",
    "sections": [{"type": "string", "content": "string"}]
  },
  "target_audience": "string",
  "key_messages": ["string"],
  "platform": "string",
  "confidence_score": "number (0-1)",
  "approval_status": "auto_approved|pending|rejected",
  "trend_references": ["uuid"],
  "created_at": "datetime"
}
```

### Content

```json
{
  "content_id": "uuid",
  "plan_id": "uuid",
  "agent_id": "uuid",
  "content_type": "text|image|video|multimodal",
  "content_url": "uri",
  "metadata": {
    "platform": "string",
    "format": "string",
    "dimensions": {"width": "integer", "height": "integer"},
    "duration": "number",
    "file_size": "integer",
    "hashtags": ["string"]
  },
  "confidence_score": "number (0-1)",
  "approval_status": "auto_approved|pending|rejected",
  "created_at": "datetime"
}
```

### Engagement

```json
{
  "engagement_id": "uuid",
  "content_id": "uuid",
  "platform": "string",
  "type": "like|comment|share|follow|view",
  "count": "integer",
  "timestamp": "datetime",
  "priority": "low|medium|high"
}
```

---

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_REQUEST` | 400 | Invalid request parameters |
| `UNAUTHORIZED` | 401 | Missing or invalid authentication |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | Resource conflict |
| `RATE_LIMIT_EXCEEDED` | 429 | Rate limit exceeded |
| `INTERNAL_ERROR` | 500 | Internal server error |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable |

---

## Rate Limiting

All APIs are rate-limited:

- **Default**: 100 requests per minute per agent
- **Trend Research**: 20 requests per minute (external API limits)
- **Content Generation**: 10 requests per minute (resource-intensive)
- **OpenClaw**: 50 requests per minute (network limits)

Rate limit headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1644000000
```

---

## Validation

All API contracts are validated using JSON Schema. See `specs/api/` for OpenAPI specifications.

**Validation Tools**:
- Pydantic models for Python validation
- JSON Schema validators for runtime validation
- OpenAPI validators for API testing

---

## References

- **Master Specification**: `specs/_meta.md`
- **Functional Specifications**: `specs/functional.md`
- **Database Schema**: `specs/database/schema.sql`
- **Skill Contracts**: `specs/skills/` and `skills/README.md`
- **OpenClaw Integration**: `specs/openclaw_integration.md`
- **Orchestrator API**: `specs/api/orchestrator.yaml`

---

**This document defines technical API contracts for Project Chimera. All implementations must conform to these specifications.**
