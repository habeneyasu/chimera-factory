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

**Key Principle**: Developer tools (MCP) are separate from runtime agent capabilities (Skills). This separation ensures that development tooling can evolve independently from agent runtime capabilities.

### Selected MCP Servers

The following MCP servers are selected and configured for Project Chimera development:

#### 1. Filesystem MCP (`@modelcontextprotocol/server-filesystem`)

**Purpose**: File system operations for reading, writing, and navigating project files.

**Capabilities**:
- Read files and directories
- Write/create files
- List directory contents
- Search files by pattern
- Get file metadata (size, permissions, timestamps)
- Move/rename files
- Delete files

**Use Cases**:
- Reading specification files before implementing code
- Creating new files following project structure
- Navigating codebase to understand architecture
- Searching for specific patterns or code references
- Managing test files and fixtures

**Configuration**:
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/home/haben/Project/KAIM-Training-Portfolio/chimera-factory"
      ]
    }
  }
}
```

**Available Tools**: 15+ tools including:
- `read_file`: Read file contents
- `write_file`: Write/create files
- `list_directory`: List directory contents
- `search_files`: Search files by pattern
- `get_file_info`: Get file metadata
- `move_file`: Move/rename files
- `create_directory`: Create directories

**Example Usage**:
```
@filesystem read specs/technical.md
@filesystem list_directory specs/
@filesystem search_files pattern="*.py" path=src/
```

---

#### 2. GitHub MCP (`@modelcontextprotocol/server-github`)

**Purpose**: GitHub API operations for repository management, issues, pull requests, and collaboration.

**Capabilities**:
- Repository operations (read, create, update)
- Issue management (create, list, update, close)
- Pull request operations (create, review, merge)
- Branch management
- Commit history and diffs
- File operations via GitHub API
- Search repositories and code

**Use Cases**:
- Creating issues for bugs or features
- Managing pull requests and code reviews
- Reading repository documentation
- Checking commit history and changes
- Searching code across repositories
- Managing project boards and milestones

**Configuration**:
```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-github"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

**Environment Variables Required**:
- `GITHUB_TOKEN`: GitHub Personal Access Token with appropriate scopes:
  - `repo` (full repository access)
  - `read:org` (read organization membership)
  - `read:user` (read user profile)

**Available Tools**: 26+ tools including:
- `get_repository`: Get repository information
- `list_issues`: List repository issues
- `create_issue`: Create new issue
- `get_pull_request`: Get PR details
- `create_pull_request`: Create new PR
- `list_commits`: List repository commits
- `search_code`: Search code across repositories
- `get_file_contents`: Get file contents from repository

**Example Usage**:
```
@github get repository habeneyasu/chimera-factory
@github list issues habeneyasu/chimera-factory state=open
@github create issue habeneyasu/chimera-factory title="Feature: Add new skill" body="Description"
@github search code query="trend research" repo=habeneyasu/chimera-factory
```

---

#### 3. PostgreSQL MCP (`@modelcontextprotocol/server-postgres`)

**Purpose**: Database operations during development for schema queries, migrations, and data inspection.

**Capabilities**:
- Execute SQL queries
- List tables and schemas
- Describe table structures
- Run migrations
- Inspect database metadata
- Query data for testing and debugging

**Use Cases**:
- Verifying database schema matches `specs/database/schema.sql`
- Running test queries during development
- Inspecting data for debugging
- Validating migrations
- Checking table relationships and constraints

**Configuration**:
```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-postgres"
      ],
      "env": {
        "POSTGRES_CONNECTION_STRING": "${POSTGRES_CONNECTION_STRING}"
      }
    }
  }
}
```

**Environment Variables Required**:
- `POSTGRES_CONNECTION_STRING`: PostgreSQL connection string
  - Format: `postgresql://user:password@host:port/database`
  - Example: `postgresql://chimera:password@localhost:5432/chimera_dev`

**Available Tools**: 10+ tools including:
- `query`: Execute SQL query
- `list_tables`: List all tables
- `describe_table`: Get table schema
- `list_schemas`: List database schemas
- `get_table_info`: Get detailed table information

**Example Usage**:
```
@postgres query "SELECT * FROM agents LIMIT 10"
@postgres list_tables
@postgres describe_table table_name=content
@postgres query "SELECT COUNT(*) FROM content WHERE status = 'pending'"
```

**Security Note**: PostgreSQL MCP should only be used in development. Production database access should use application-level connection pooling and proper authentication.

---

### Complete MCP Configuration

**Location**: `.cursor/mcp.json` (project root)

**Full Configuration Example**:
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/home/haben/Project/KAIM-Training-Portfolio/chimera-factory"
      ]
    },
    "github": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-github"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "postgres": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-postgres"
      ],
      "env": {
        "POSTGRES_CONNECTION_STRING": "${POSTGRES_CONNECTION_STRING}"
      }
    }
  }
}
```

**Environment Variables** (`.env` file, not committed):
```bash
# GitHub MCP
GITHUB_TOKEN=ghp_your_personal_access_token_here

# PostgreSQL MCP
POSTGRES_CONNECTION_STRING=postgresql://chimera:password@localhost:5432/chimera_dev
```

---

### Setup Instructions

#### Step 1: Install Prerequisites

```bash
# Verify Node.js and npx are installed
node --version  # Should be v18+
npx --version
```

#### Step 2: Create MCP Configuration

1. Create `.cursor/mcp.json` in project root
2. Copy the configuration example above
3. Adjust file paths and environment variable names as needed

#### Step 3: Configure Environment Variables

1. Create `.env` file in project root (add to `.gitignore`)
2. Add required environment variables:
   - `GITHUB_TOKEN`: Generate from GitHub → Settings → Developer settings → Personal access tokens
   - `POSTGRES_CONNECTION_STRING`: Your local PostgreSQL connection string

#### Step 4: Verify Installation

1. Restart Cursor IDE
2. Check Settings → Tools & MCP
3. Verify all three servers show as "Enabled"
4. Test each server:
   - `@filesystem list_directory .`
   - `@github get repository habeneyasu/chimera-factory`
   - `@postgres list_tables`

---

### Development Workflow Integration

#### Before Writing Code

1. **Read Specs**: Use Filesystem MCP to read specification files
   ```
   @filesystem read specs/_meta.md
   @filesystem read specs/functional.md
   @filesystem read specs/technical.md
   ```

2. **Check Database Schema**: Use PostgreSQL MCP to verify schema
   ```
   @postgres describe_table table_name=content
   @postgres query "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'content'"
   ```

3. **Review Related Code**: Use Filesystem MCP to find related implementations
   ```
   @filesystem search_files pattern="*.py" path=src/
   ```

#### During Development

1. **Create Files**: Use Filesystem MCP to create new files following project structure
2. **Check GitHub**: Use GitHub MCP to reference issues, PRs, or documentation
3. **Test Database**: Use PostgreSQL MCP to test queries and verify data

#### After Development

1. **Create Issues/PRs**: Use GitHub MCP to create issues or pull requests
2. **Verify Schema**: Use PostgreSQL MCP to ensure database changes are correct
3. **Document Changes**: Use Filesystem MCP to update documentation

---

### Key Characteristics

- **When**: Used during development and testing
- **Who**: Developers and CI/CD pipelines
- **Purpose**: Tooling, debugging, data access
- **Examples**: Git operations, file system access, database queries
- **Configuration**: `.cursor/mcp.json` (project-specific)
- **Lifecycle**: Development-time only, not included in runtime deployments

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
