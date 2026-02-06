# OpenClaw Network Integration: Project Chimera

**Prepared By**: habeneyasu  
**Repository**: [https://github.com/habeneyasu/chimera-factory](https://github.com/habeneyasu/chimera-factory)  
**Last Updated**: February 2026  
**Version**: 1.0.0

---

## Overview

This document defines the detailed integration plan for Project Chimera's participation in the OpenClaw agent social network. OpenClaw enables AI agents to discover, communicate, and collaborate with each other, creating a networked ecosystem of autonomous agents.

**Reference**: See `specs/_meta.md` for architectural constraints and `specs/functional.md` for user stories (US-013 to US-016).

---

## Integration Architecture

### MCP-Based Integration

Project Chimera uses **Model Context Protocol (MCP)** as the universal interface to OpenClaw:

- **MCP Resources**: Agent capabilities and status (read-only data)
- **MCP Tools**: Network operations (publish, discover, collaborate)
- **MCP Prompts**: Standardized communication templates

### Integration Components

```
┌─────────────────────────────────────────────────────────┐
│              Chimera Agent Orchestrator                  │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Status       │  │ Capability   │  │ Network      │  │
│  │ Manager      │  │ Publisher    │  │ Discovery    │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                  │           │
│         └─────────────────┴──────────────────┘           │
│                          │                               │
│                    ┌─────▼──────┐                        │
│                    │ MCP Bridge │                        │
│                    │  (OpenClaw)│                        │
│                    └─────┬──────┘                        │
└──────────────────────────┼──────────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │ OpenClaw    │
                    │   Network   │
                    └─────────────┘
```

---

## 1. Publishing Agent Availability and Status

### 1.1 Status Publication Mechanism

Chimera agents publish their availability and status to OpenClaw in real-time using MCP Resources.

#### Status Update Triggers

Status is published automatically when:

1. **Agent State Changes**:
   - Agent starts/stops
   - Agent transitions between states (idle → researching → generating → engaging)
   - Agent enters sleep mode

2. **Resource Availability Changes**:
   - CPU usage crosses thresholds (e.g., < 20% → available, > 80% → busy)
   - Memory usage changes significantly
   - Queue depth changes (empty → available, full → busy)

3. **Capability Changes**:
   - New skills become available
   - Skills become unavailable (maintenance, errors)
   - Skill performance metrics change

4. **Periodic Heartbeat**:
   - Every 30 seconds: Lightweight status update (status only)
   - Every 5 minutes: Full status update (status + resources + capabilities)

#### Status Publication Format

**MCP Resource**: `openclaw://agent/{agent_id}/status`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "agent_id": {
      "type": "string",
      "format": "uuid",
      "description": "Unique agent identifier"
    },
    "agent_name": {
      "type": "string",
      "description": "Human-readable agent name"
    },
    "status": {
      "type": "string",
      "enum": ["idle", "researching", "generating", "engaging", "sleeping", "error"],
      "description": "Current operational status"
    },
    "availability": {
      "type": "string",
      "enum": ["available", "busy", "unavailable"],
      "description": "Availability for new tasks"
    },
    "capabilities": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "skill_id": {
            "type": "string",
            "enum": ["trend_research", "content_generation", "engagement_management"]
          },
          "status": {
            "type": "string",
            "enum": ["available", "busy", "unavailable"]
          },
          "performance_metrics": {
            "type": "object",
            "properties": {
              "avg_response_time_ms": {
                "type": "integer"
              },
              "success_rate": {
                "type": "number",
                "minimum": 0,
                "maximum": 1
              },
              "queue_depth": {
                "type": "integer",
                "minimum": 0
              }
            }
          }
        },
        "required": ["skill_id", "status"]
      }
    },
    "resources": {
      "type": "object",
      "properties": {
        "cpu_usage_percent": {
          "type": "number",
          "minimum": 0,
          "maximum": 100
        },
        "memory_usage_percent": {
          "type": "number",
          "minimum": 0,
          "maximum": 100
        },
        "queue_depth": {
          "type": "integer",
          "minimum": 0
        },
        "max_concurrent_tasks": {
          "type": "integer",
          "minimum": 1
        },
        "available_slots": {
          "type": "integer",
          "minimum": 0
        }
      },
      "required": ["cpu_usage_percent", "memory_usage_percent", "queue_depth"]
    },
    "reputation": {
      "type": "object",
      "properties": {
        "score": {
          "type": "number",
          "minimum": 0,
          "maximum": 1
        },
        "total_collaborations": {
          "type": "integer",
          "minimum": 0
        },
        "success_rate": {
          "type": "number",
          "minimum": 0,
          "maximum": 1
        }
      }
    },
    "last_updated": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp of last status update"
    },
    "network_endpoint": {
      "type": "string",
      "format": "uri",
      "description": "MCP endpoint for direct communication"
    }
  },
  "required": ["agent_id", "agent_name", "status", "availability", "capabilities", "resources", "last_updated"]
}
```

### 1.2 Status Update Implementation

#### API Endpoint

**POST** `/api/v1/openclaw/publish` (See `specs/technical.md` for full API contract)

#### Implementation Flow

```python
# Pseudo-code for status publication
def publish_status_to_openclaw(agent_id: UUID) -> None:
    """
    Publish agent status to OpenClaw network via MCP.
    """
    # 1. Gather current agent state
    agent_state = get_agent_state(agent_id)
    resource_metrics = get_resource_metrics(agent_id)
    capabilities = get_agent_capabilities(agent_id)
    reputation = get_agent_reputation(agent_id)
    
    # 2. Construct status payload
    status_payload = {
        "agent_id": str(agent_id),
        "agent_name": agent_state.name,
        "status": agent_state.current_status,
        "availability": calculate_availability(resource_metrics),
        "capabilities": format_capabilities(capabilities),
        "resources": format_resources(resource_metrics),
        "reputation": reputation,
        "last_updated": datetime.utcnow().isoformat(),
        "network_endpoint": get_mcp_endpoint(agent_id)
    }
    
    # 3. Publish via MCP Resource
    mcp_client.publish_resource(
        uri=f"openclaw://agent/{agent_id}/status",
        content=status_payload,
        ttl=60  # Time-to-live: 60 seconds
    )
    
    # 4. Log publication
    log_network_activity(
        agent_id=agent_id,
        action="status_published",
        payload=status_payload
    )
```

### 1.3 Availability Calculation

Availability is calculated based on resource metrics:

```python
def calculate_availability(resources: ResourceMetrics) -> str:
    """
    Calculate availability status based on resource metrics.
    """
    # High resource usage = busy
    if (resources.cpu_usage_percent > 80 or 
        resources.memory_usage_percent > 80 or
        resources.queue_depth >= resources.max_concurrent_tasks):
        return "busy"
    
    # Low resources = unavailable
    if (resources.cpu_usage_percent > 95 or
        resources.memory_usage_percent > 95):
        return "unavailable"
    
    # Otherwise available
    return "available"
```

### 1.4 Status Update Frequency

| Update Type | Frequency | Trigger | Payload Size |
|------------|-----------|---------|--------------|
| **Heartbeat** | Every 30 seconds | Periodic | Light (status only) |
| **State Change** | Immediate | On state transition | Medium (status + availability) |
| **Resource Change** | Every 5 minutes | Periodic | Full (all fields) |
| **Capability Change** | Immediate | On capability change | Medium (capabilities + status) |

---

## 2. Capability Advertisement

### 2.1 Capability Publication

Chimera agents advertise their available skills (capabilities) to the OpenClaw network.

#### Capability Resource Format

**MCP Resource**: `openclaw://agent/{agent_id}/capabilities`

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
        "type": "object",
        "properties": {
          "skill_id": {
            "type": "string",
            "enum": ["trend_research", "content_generation", "engagement_management"]
          },
          "skill_name": {
            "type": "string",
            "description": "Human-readable skill name"
          },
          "description": {
            "type": "string",
            "description": "What this skill can do"
          },
          "input_schema": {
            "type": "object",
            "description": "JSON Schema for skill input"
          },
          "output_schema": {
            "type": "object",
            "description": "JSON Schema for skill output"
          },
          "status": {
            "type": "string",
            "enum": ["available", "busy", "unavailable"]
          },
          "performance_metrics": {
            "type": "object",
            "properties": {
              "avg_response_time_ms": {
                "type": "integer"
              },
              "success_rate": {
                "type": "number",
                "minimum": 0,
                "maximum": 1
              },
              "total_invocations": {
                "type": "integer",
                "minimum": 0
              }
            }
          },
          "rate_limits": {
            "type": "object",
            "properties": {
              "requests_per_minute": {
                "type": "integer"
              },
              "requests_per_hour": {
                "type": "integer"
              }
            }
          }
        },
        "required": ["skill_id", "skill_name", "description", "status"]
      }
    },
    "published_at": {
      "type": "string",
      "format": "date-time"
    }
  },
  "required": ["agent_id", "capabilities", "published_at"]
}
```

### 2.2 Capability Update Triggers

Capabilities are republished when:

1. **Skill Availability Changes**: Skill becomes available/unavailable
2. **Performance Metrics Update**: Significant change in success rate or response time
3. **Schema Changes**: Input/output schema is updated
4. **Periodic Refresh**: Every 15 minutes to ensure network has current information

---

## 3. Network Discovery

### 3.1 Agent Discovery

Chimera agents can discover other agents in the OpenClaw network by querying capabilities.

#### Discovery Query Format

**MCP Tool**: `openclaw.discover_agents`

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
      "description": "Required capabilities (trend_research, content_generation, etc.)"
    },
    "status": {
      "type": "string",
      "enum": ["idle", "available"],
      "description": "Filter by agent status"
    },
    "min_reputation": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "description": "Minimum reputation score"
    },
    "max_response_time_ms": {
      "type": "integer",
      "description": "Maximum acceptable response time"
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

#### Discovery Response Format

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "agents": {
      "type": "array",
      "items": {
        "$ref": "#/definitions/AgentStatus"
      }
    },
    "total_found": {
      "type": "integer"
    },
    "query_id": {
      "type": "string",
      "format": "uuid"
    }
  },
  "required": ["agents", "total_found"]
}
```

### 3.2 Trend Discovery

Chimera agents can discover trends shared by other agents in the network.

**MCP Resource**: `openclaw://trends/{trend_id}`

**MCP Tool**: `openclaw.discover_trends`

```json
{
  "topic": "string",
  "sources": ["string"],
  "timeframe": "1h|24h|7d|30d",
  "min_engagement": "number",
  "limit": "integer"
}
```

---

## 4. Collaboration Protocols

### 4.1 Collaboration Request

Chimera agents can request collaboration from other agents.

**MCP Tool**: `openclaw.request_collaboration`

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
      "enum": ["trend_research", "content_generation", "engagement_management"]
    },
    "input_data": {
      "type": "object",
      "description": "Task input data"
    },
    "deadline": {
      "type": "string",
      "format": "date-time"
    },
    "compensation": {
      "type": "object",
      "properties": {
        "amount": {
          "type": "number"
        },
        "currency": {
          "type": "string"
        }
      },
      "description": "Optional compensation for collaboration"
    }
  },
  "required": ["requester_agent_id", "target_agent_id", "task", "required_capability"]
}
```

### 4.2 Collaboration Response

Target agents respond to collaboration requests.

```json
{
  "collaboration_id": "uuid",
  "status": "accepted|rejected|pending",
  "response": {
    "estimated_completion": "datetime",
    "cost": "number",
    "terms": "object"
  }
}
```

---

## 5. Trend Sharing

### 5.1 Publishing Trends to Network

Chimera agents can share discovered trends with the OpenClaw network.

**MCP Resource**: `openclaw://trends/{trend_id}`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "trend_id": {
      "type": "string",
      "format": "uuid"
    },
    "title": {
      "type": "string"
    },
    "source": {
      "type": "string",
      "enum": ["twitter", "youtube", "news", "reddit"]
    },
    "topic": {
      "type": "string"
    },
    "engagement": {
      "type": "number"
    },
    "relevance_score": {
      "type": "number",
      "minimum": 0,
      "maximum": 1
    },
    "velocity": {
      "type": "number"
    },
    "hashtags": {
      "type": "array",
      "items": {
        "type": "string"
      }
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
        },
        "discovered_at": {
          "type": "string",
          "format": "date-time"
        }
      }
    },
    "published_at": {
      "type": "string",
      "format": "date-time"
    }
  },
  "required": ["trend_id", "title", "source", "topic", "attribution", "published_at"]
}
```

### 5.2 Trend Attribution

When using trends from other agents, Chimera agents must:

1. **Credit the Source**: Include attribution in content metadata
2. **Link to Original**: Reference the original trend resource
3. **Respect Licensing**: Follow any usage terms specified by the source agent

---

## 6. Implementation Details

### 6.1 MCP Server Configuration

OpenClaw integration requires an MCP server configured as follows:

```json
{
  "mcpServers": {
    "openclaw": {
      "command": "npx",
      "args": ["-y", "@openclaw/mcp-server"],
      "env": {
        "OPENCLAW_NETWORK_URL": "https://network.openclaw.io",
        "OPENCLAW_AGENT_ID": "${AGENT_ID}",
        "OPENCLAW_API_KEY": "${API_KEY}"
      }
    }
  }
}
```

### 6.2 Status Update Service

A dedicated service manages status publication:

```python
class OpenClawStatusService:
    """
    Service for managing agent status publication to OpenClaw.
    """
    
    def __init__(self, mcp_client: MCPClient, agent_id: UUID):
        self.mcp_client = mcp_client
        self.agent_id = agent_id
        self.last_full_update = None
        self.status_cache = {}
    
    async def start_heartbeat(self):
        """Start periodic status updates."""
        while True:
            await self.publish_heartbeat()
            await asyncio.sleep(30)  # 30 seconds
    
    async def publish_heartbeat(self):
        """Publish lightweight status update."""
        status = await self.get_current_status()
        await self.mcp_client.publish_resource(
            uri=f"openclaw://agent/{self.agent_id}/status",
            content=status,
            ttl=60
        )
    
    async def publish_full_status(self):
        """Publish complete status update."""
        status = await self.get_full_status()
        await self.mcp_client.publish_resource(
            uri=f"openclaw://agent/{self.agent_id}/status",
            content=status,
            ttl=300  # 5 minutes
        )
        self.last_full_update = datetime.utcnow()
    
    async def on_state_change(self, new_state: str):
        """Handle state change event."""
        await self.publish_full_status()
        await self.log_state_change(new_state)
```

### 6.3 Error Handling

Status publication failures are handled gracefully:

1. **Retry Logic**: Exponential backoff for transient failures
2. **Fallback**: Cache status locally if network unavailable
3. **Monitoring**: Alert on repeated failures
4. **Degradation**: Continue operation even if status publication fails

---

## 7. Security and Governance

### 7.1 Authentication

- **API Keys**: Secure API key management for OpenClaw network access
- **Agent Identity**: Cryptographic agent identity verification
- **Rate Limiting**: Respect network rate limits

### 7.2 Privacy

- **Selective Sharing**: Agents can control what information is shared
- **Data Minimization**: Only share necessary information for discovery
- **Audit Logging**: All network interactions are logged

### 7.3 Trust and Reputation

- **Reputation System**: Track and report agent reputation scores
- **Quality Signals**: Share performance metrics to build trust
- **Attribution**: Always credit sources when using network resources

---

## 8. Monitoring and Observability

### 8.1 Metrics

Track the following metrics:

- **Status Publication Rate**: Updates per minute
- **Network Reachability**: Success rate of status publications
- **Discovery Queries**: Number of discovery requests
- **Collaborations**: Number of collaboration requests/responses
- **Trend Shares**: Number of trends shared/discovered

### 8.2 Logging

All network activities are logged:

```python
log_network_activity(
    agent_id=agent_id,
    action="status_published",
    target="openclaw_network",
    payload=status_payload,
    timestamp=datetime.utcnow(),
    success=True
)
```

---

## 9. Testing Strategy

### 9.1 Unit Tests

- Test status calculation logic
- Test availability calculation
- Test capability formatting
- Test error handling

### 9.2 Integration Tests

- Test MCP resource publication
- Test discovery queries
- Test collaboration requests
- Test network connectivity

### 9.3 End-to-End Tests

- Test full status publication flow
- Test agent discovery and collaboration
- Test trend sharing and attribution

---

## 10. Future Enhancements

### Phase 2 Features

1. **Economic Integration**: Agent-to-agent payments via Coinbase AgentKit
2. **Advanced Discovery**: Semantic search for agents by capability description
3. **Collaboration Marketplace**: Public marketplace for agent services
4. **Network Analytics**: Dashboard for network participation metrics

---

## References

- **Master Specification**: `specs/_meta.md`
- **Functional Specifications**: `specs/functional.md` (US-013 to US-016)
- **Technical Specifications**: `specs/technical.md` (OpenClaw Integration API)
- **Architecture Strategy**: `research/architecture_strategy.md`
- **Submission Report**: `research/submission_report_feb4.md`

---

**This document defines the complete OpenClaw integration plan for Project Chimera, including detailed status publication mechanisms, capability advertisement, discovery protocols, and collaboration workflows.**
