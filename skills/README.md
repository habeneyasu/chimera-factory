# Agent Skills: Project Chimera

**Prepared By**: habeneyasu  
**Repository**: [https://github.com/habeneyasu/chimera-factory](https://github.com/habeneyasu/chimera-factory)

## Overview

Skills are reusable capability packages that the Chimera Agent invokes during runtime to perform specific tasks. Each skill defines clear Input/Output contracts and dependencies.

## Skill Architecture

### Skill Definition Requirements

Each skill must include:
1. **README.md**: Documentation with use cases and examples
2. **contract.json**: JSON Schema for Input/Output validation
3. **__init__.py**: Python interface implementation (to be created in Task 2.3)

### Skill Interface Contract

```python
from typing import Dict, Any, Optional
from pydantic import BaseModel

class SkillInput(BaseModel):
    """Input contract for skill execution"""
    pass

class SkillOutput(BaseModel):
    """Output contract for skill execution"""
    pass

class SkillError(Exception):
    """Base exception for skill errors"""
    pass

def execute(input_data: SkillInput) -> SkillOutput:
    """
    Execute the skill with given input.
    
    Args:
        input_data: Validated input according to contract
        
    Returns:
        Validated output according to contract
        
    Raises:
        SkillError: If skill execution fails
    """
    pass
```

## Critical Skills

### 1. skill_trend_research

**Purpose**: Research trending topics from multiple sources (Twitter, News APIs, Reddit)

**Input Contract**:
```json
{
  "type": "object",
  "properties": {
    "topic": {
      "type": "string",
      "description": "Topic or keyword to research"
    },
    "sources": {
      "type": "array",
      "items": {"type": "string"},
      "description": "List of sources to query (twitter, news, reddit)"
    },
    "timeframe": {
      "type": "string",
      "enum": ["1h", "24h", "7d", "30d"],
      "description": "Time window for trend analysis"
    }
  },
  "required": ["topic", "sources"]
}
```

**Output Contract**:
```json
{
  "type": "object",
  "properties": {
    "trends": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "title": {"type": "string"},
          "source": {"type": "string"},
          "engagement": {"type": "number"},
          "timestamp": {"type": "string"}
        }
      }
    },
    "confidence": {
      "type": "number",
      "minimum": 0,
      "maximum": 1
    }
  },
  "required": ["trends", "confidence"]
}
```

**MCP Dependencies**:
- `mcp-server-twitter`: Twitter API access
- `mcp-server-news`: News aggregation
- `mcp-server-reddit`: Reddit API access

**Status**: 📋 **To be implemented in Task 2.3**

---

### 2. skill_content_generate

**Purpose**: Generate multimodal content (text captions, images, videos) based on trends and persona

**Input Contract**:
```json
{
  "type": "object",
  "properties": {
    "content_type": {
      "type": "string",
      "enum": ["text", "image", "video", "multimodal"]
    },
    "prompt": {
      "type": "string",
      "description": "Content generation prompt"
    },
    "style": {
      "type": "string",
      "description": "Persona style guide reference"
    },
    "character_reference_id": {
      "type": "string",
      "description": "Character consistency lock ID"
    }
  },
  "required": ["content_type", "prompt"]
}
```

**Output Contract**:
```json
{
  "type": "object",
  "properties": {
    "content_url": {
      "type": "string",
      "description": "URL or path to generated content"
    },
    "metadata": {
      "type": "object",
      "properties": {
        "platform": {"type": "string"},
        "format": {"type": "string"},
        "dimensions": {"type": "object"},
        "duration": {"type": "number"}
      }
    },
    "confidence": {
      "type": "number",
      "minimum": 0,
      "maximum": 1
    }
  },
  "required": ["content_url", "metadata", "confidence"]
}
```

**MCP Dependencies**:
- `mcp-server-ideogram`: Image generation
- `mcp-server-runway`: Video generation
- `mcp-server-midjourney`: Alternative image generation

**Status**: 📋 **To be implemented in Task 2.3**

---

### 3. skill_engagement_manage

**Purpose**: Manage social media engagement (replies, likes, follows, comments)

**Input Contract**:
```json
{
  "type": "object",
  "properties": {
    "action": {
      "type": "string",
      "enum": ["reply", "like", "follow", "comment", "share"]
    },
    "platform": {
      "type": "string",
      "enum": ["twitter", "instagram", "tiktok", "threads"]
    },
    "target": {
      "type": "string",
      "description": "Target post/comment/user ID"
    },
    "content": {
      "type": "string",
      "description": "Content for reply/comment (if applicable)"
    },
    "persona_constraints": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Persona constraints to apply"
    }
  },
  "required": ["action", "platform", "target"]
}
```

**Output Contract**:
```json
{
  "type": "object",
  "properties": {
    "status": {
      "type": "string",
      "enum": ["success", "pending", "failed"]
    },
    "engagement_id": {
      "type": "string",
      "description": "ID of created engagement"
    },
    "platform_response": {
      "type": "object",
      "description": "Raw response from platform API"
    }
  },
  "required": ["status"]
}
```

**MCP Dependencies**:
- `mcp-server-twitter`: Twitter API
- `mcp-server-instagram`: Instagram API
- `mcp-server-tiktok`: TikTok API

**Status**: 📋 **To be implemented in Task 2.3**

---

## Skill Development Guidelines

1. **Contract-First**: Define Input/Output contracts before implementation
2. **Error Handling**: All skills must handle errors gracefully
3. **Idempotency**: Skills should be idempotent when possible
4. **Logging**: All skill executions must be logged
5. **Testing**: Each skill must have corresponding tests in `tests/`

## Directory Structure

```
skills/
├── README.md                    # This file
├── skill_trend_research/
│   ├── README.md                # Skill documentation
│   ├── contract.json            # Input/Output schema
│   └── __init__.py              # Implementation (Task 2.3)
├── skill_content_generate/
│   ├── README.md
│   ├── contract.json
│   └── __init__.py
└── skill_engagement_manage/
    ├── README.md
    ├── contract.json
    └── __init__.py
```

## Next Steps

- [ ] Create detailed README for each skill (Task 2.3)
- [ ] Define JSON Schema contracts for each skill
- [ ] Implement skill interfaces (Task 2.3)
- [ ] Create unit tests for skills (Task 3.1)

## References

- Project Chimera SRS - Section 4.3 (Creative Engine)
- Project Chimera SRS - Section 4.4 (Action System)
- `research/tooling_strategy.md` - MCP vs Skills separation
