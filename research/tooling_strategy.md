# Tooling & Skills Strategy: Project Chimera

**Prepared By**: habeneyasu  
**Repository**: [https://github.com/habeneyasu/chimera-factory](https://github.com/habeneyasu/chimera-factory)  
**Date**: February 4, 2026

**Note**: This is a strategic/architectural document that explains the conceptual separation between Developer Tools (MCP) and Agent Skills (Runtime). For detailed MCP server setup and configuration, see `docs/MCP_INTEGRATION.md`. For detailed skill definitions and contracts, see `skills/README.md`.

## Overview

This document defines the two categories of tools for Project Chimera and explains the strategic rationale for their separation:

1. **Developer Tools (MCP)**: MCP servers that help developers build and maintain the system
2. **Agent Skills (Runtime)**: Capability packages that the Chimera Agent uses at runtime

This separation is critical for maintaining clear boundaries between development tooling and runtime agent capabilities, enabling independent evolution and scaling of each layer.

## Developer Tools (MCP Servers)

### Purpose

MCP servers provide standardized interfaces for development tools, enabling the IDE and development workflow to interact with external systems. These are used exclusively during development, testing, and CI/CD operations.

### Selected MCP Servers

The following MCP servers are configured for development:

- **Filesystem MCP**: File system operations (reading, writing, directory navigation)
- **GitHub MCP**: GitHub API operations (issues, PRs, repository metadata)
- **PostgreSQL MCP**: Database operations during development (schema queries, migrations)

**Configuration Details**: See `docs/MCP_INTEGRATION.md` for complete setup instructions, configuration examples, and troubleshooting.

### Key Characteristics

- **When**: Used during development and testing
- **Who**: Developers and CI/CD pipelines
- **Purpose**: Tooling, debugging, data access
- **Examples**: Git operations, file system access, database queries

## Agent Skills (Runtime)

### Purpose

Skills are reusable capability packages that the Chimera Agent invokes during runtime to perform specific tasks. These are the agent's "hands" - the capabilities that enable autonomous behavior.

### Critical Skills

Three critical skills have been defined:

1. **skill_trend_research**: Research trending topics from multiple sources
2. **skill_content_generate**: Generate multimodal content (text, image, video)
3. **skill_engagement_manage**: Manage social media engagement (replies, likes, follows)

**Detailed Definitions**: See `skills/README.md` for complete skill contracts, input/output schemas, MCP dependencies, and implementation guidelines.

### Key Characteristics

- **When**: Used during agent runtime execution
- **Who**: Chimera Agent (Planner/Worker/Judge)
- **Purpose**: Agent actions and capabilities
- **Examples**: Trend research, content generation, engagement management

## MCP vs Skills: Clear Separation

### Why This Separation Matters

The distinction between MCP servers (development tools) and Skills (runtime capabilities) is fundamental to Project Chimera's architecture:

1. **Different Lifecycles**: MCP servers are development-time tools that may change frequently. Skills are runtime capabilities that must be stable and versioned.

2. **Different Audiences**: MCP servers serve developers. Skills serve the agent runtime.

3. **Different Scaling Models**: MCP servers scale with developer needs. Skills scale with agent workload.

4. **Different Dependencies**: MCP servers depend on development infrastructure. Skills depend on runtime infrastructure and may use runtime MCP servers.

### MCP Servers (Development Tools)

| Aspect | Description |
|--------|-------------|
| **When** | Used during development and testing |
| **Who** | Developers and CI/CD pipelines |
| **Purpose** | Tooling, debugging, data access |
| **Examples** | Git operations, file system access, database queries |
| **Configuration** | `.cursor/mcp.json` (project-specific) |

### Skills (Runtime Capabilities)

| Aspect | Description |
|--------|-------------|
| **When** | Used during agent runtime execution |
| **Who** | Chimera Agent (Planner/Worker/Judge) |
| **Purpose** | Agent actions and capabilities |
| **Examples** | Trend research, content generation, engagement management |
| **Configuration** | `skills/` directory with contracts and implementations |

### Runtime MCP Servers

**Important Note**: Skills may depend on runtime MCP servers (e.g., Twitter MCP, Instagram MCP, Image Generation MCP) that are different from development MCP servers. These runtime MCP servers are configured separately and used by the agent during execution, not by developers during development.

## Integration Architecture

The following diagram illustrates the separation between development and runtime environments:

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
│  │  - PostgreSQL MCP             │ │
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
│  │  - skill_trend_research       │ │
│  │  - skill_content_generate     │ │
│  │  - skill_engagement_manage    │ │
│  └──────────┬───────────────────┘ │
│             │                      │
│  ┌──────────▼───────────────────┐ │
│  │  MCP Servers (Runtime)       │ │
│  │  - Twitter MCP                │ │
│  │  - Instagram MCP              │ │
│  │  - News MCP                    │ │
│  │  - Image Gen MCP               │ │
│  └──────────────────────────────┘ │
└─────────────────────────────────────┘
```

## Strategic Benefits

This separation provides several strategic benefits:

1. **Clear Boundaries**: Developers know which tools to use for development. Agents know which capabilities to use at runtime.

2. **Independent Evolution**: MCP servers can be updated without affecting runtime skills. Skills can evolve without impacting development tooling.

3. **Scalability**: Development tools scale with team size. Runtime skills scale with agent workload.

4. **Security**: Development tools have different security requirements than runtime capabilities.

5. **Testing**: Development tools can be tested independently from runtime skills.

## Next Steps

- [x] Define MCP vs Skills separation (Task 1) ✅
- [x] Create skills directory structure (Task 2) ✅
- [ ] Implement skill interfaces (Task 2.3)
- [ ] Configure runtime MCP servers for agent execution (Task 3)
- [ ] Implement MCP server connections in Docker environment (Task 3)

## References

- **MCP Setup & Configuration**: `docs/MCP_INTEGRATION.md`
- **Skill Definitions & Contracts**: `skills/README.md`
- **Model Context Protocol Documentation**: https://modelcontextprotocol.io
- **MCP Server Registry**: https://github.com/modelcontextprotocol/servers
- **Project Chimera SRS Document** - Section 3.2 (MCP Integration Layer)
