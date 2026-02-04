# Tooling & Skills Strategy: Project Chimera

**Prepared By**: habeneyasu  
**Repository**: [https://github.com/habeneyasu/chimera-factory](https://github.com/habeneyasu/chimera-factory)  
**Date**: February 4, 2025

## Overview

This document defines the two categories of tools for Project Chimera:
1. **Developer Tools (MCP)**: MCP servers that help developers build and maintain the system
2. **Agent Skills (Runtime)**: Capability packages that the Chimera Agent uses at runtime

## Developer Tools (MCP Servers)

### Purpose
MCP servers provide standardized interfaces for development tools, enabling the IDE and development workflow to interact with external systems.

### Selected MCP Servers

#### 1. **Filesystem MCP Server** (Development)
**Purpose**: File system operations via MCP
**Use Cases**:
- File reading/writing
- Directory operations
- File search and navigation

**Configuration**:
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/haben/Project/KAIM-Training-Portfolio/chimera-factory"]
    }
  }
}
```

#### 2. **PostgreSQL MCP Server** (Development)
**Purpose**: Database operations during development
**Use Cases**:
- Schema queries
- Test data management
- Database migrations

**Configuration**:
```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_CONNECTION_STRING": "${POSTGRES_CONNECTION_STRING}"
      }
    }
  }
}
```

#### 3. **GitHub MCP Server** (Development)
**Purpose**: GitHub API operations
**Use Cases**:
- Issue management
- PR operations
- Repository metadata

**Configuration**:
```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

### MCP Configuration Location

For Cursor IDE, MCP servers are configured in:
- **macOS**: `~/Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`
- **Linux**: `~/.config/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`
- **Windows**: `%APPDATA%\Cursor\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json`

### Installation Notes

1. MCP servers are installed via `npx` (Node.js required)
2. Environment variables should be set in `.env` file (not committed)
3. Each MCP server exposes Tools, Resources, and Prompts via the MCP protocol

## Agent Skills (Runtime)

### Purpose
Skills are reusable capability packages that the Chimera Agent invokes during runtime to perform specific tasks.

### Skill Definition Structure

Each skill must define:
- **Input Contract**: JSON schema for input parameters
- **Output Contract**: JSON schema for return values
- **Error Handling**: Expected error types and handling
- **Dependencies**: Required MCP servers or external services

### Critical Skills (To be implemented in Task 2.3)

#### 1. **skill_trend_research**
**Purpose**: Research trending topics from multiple sources
**Input**: `{ "topic": str, "sources": List[str], "timeframe": str }`
**Output**: `{ "trends": List[Trend], "confidence": float }`
**MCP Dependencies**: News MCP server, Twitter MCP server

#### 2. **skill_content_generate**
**Purpose**: Generate multimodal content (text, image, video)
**Input**: `{ "content_type": str, "prompt": str, "style": str }`
**Output**: `{ "content_url": str, "metadata": dict }`
**MCP Dependencies**: Image generation MCP, Video generation MCP

#### 3. **skill_engagement_manage**
**Purpose**: Manage social media engagement (replies, likes, follows)
**Input**: `{ "action": str, "target": str, "content": str }`
**Output**: `{ "status": str, "engagement_id": str }`
**MCP Dependencies**: Twitter MCP, Instagram MCP, TikTok MCP

### Skills Directory Structure

```
skills/
├── README.md                    # Skills overview and contracts
├── skill_trend_research/
│   ├── README.md                # Skill documentation
│   ├── __init__.py              # Skill interface
│   └── contract.json            # Input/Output schema
├── skill_content_generate/
│   ├── README.md
│   ├── __init__.py
│   └── contract.json
└── skill_engagement_manage/
    ├── README.md
    ├── __init__.py
    └── contract.json
```

## MCP vs Skills: Clear Separation

### MCP Servers (Development Tools)
- **When**: Used during development and testing
- **Who**: Developers and CI/CD pipelines
- **Purpose**: Tooling, debugging, data access
- **Examples**: Git operations, file system access, database queries

### Skills (Runtime Capabilities)
- **When**: Used during agent runtime execution
- **Who**: Chimera Agent (Planner/Worker/Judge)
- **Purpose**: Agent actions and capabilities
- **Examples**: Trend research, content generation, engagement management

## Integration Architecture

```
┌─────────────────────────────────────┐
│     Development Environment         │
│  ┌───────────────────────────────┐ │
│  │  Cursor IDE                    │ │
│  │  ┌──────────────────────────┐ │ │
│  │  │  MCP Client              │ │ │
│  │  └──────────┬───────────────┘ │ │
│  └─────────────┼─────────────────┘ │
│                │                    │
│  ┌─────────────▼─────────────────┐ │
│  │  MCP Servers (Dev Tools)      │ │
│  │  - Filesystem MCP             │ │
│  │  - PostgreSQL MCP            │ │
│  │  - GitHub MCP                 │ │
│  └───────────────────────────────┘ │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│     Runtime Environment             │
│  ┌───────────────────────────────┐ │
│  │  Chimera Agent                │ │
│  │  ┌──────────────────────────┐ │ │
│  │  │  Planner/Worker/Judge    │ │ │
│  │  └──────────┬───────────────┘ │ │
│  └─────────────┼─────────────────┘ │
│                │                    │
│  ┌─────────────▼─────────────────┐ │
│  │  Skills (Runtime)             │ │
│  │  - skill_trend_research      │ │
│  │  - skill_content_generate    │ │
│  │  - skill_engagement_manage   │ │
│  └──────────┬───────────────────┘ │
│             │                      │
│  ┌──────────▼───────────────────┐ │
│  │  MCP Servers (Runtime)       │ │
│  │  - Twitter MCP               │ │
│  │  - Instagram MCP              │ │
│  │  - News MCP                   │ │
│  │  - Image Gen MCP              │ │
│  └──────────────────────────────┘ │
└─────────────────────────────────────┘
```

## Next Steps

1. **Task 2.3**: Create skills directory structure with README for 3 critical skills
2. **Task 2.3**: Document MCP server configuration in this file
3. **Task 3**: Implement MCP server connections in Docker environment
4. **Runtime**: Configure runtime MCP servers for agent execution

## References

- [Model Context Protocol Documentation](https://modelcontextprotocol.io)
- [MCP Server Registry](https://github.com/modelcontextprotocol/servers)
- Project Chimera SRS Document - Section 3.2 (MCP Integration Layer)
