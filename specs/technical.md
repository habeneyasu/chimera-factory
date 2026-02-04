# Technical Specifications: Project Chimera

**Prepared By**: habeneyasu  
**Repository**: [https://github.com/habeneyasu/chimera-factory](https://github.com/habeneyasu/chimera-factory)

## Overview

This document defines the technical architecture, API contracts, and system interfaces for Project Chimera using executable schemas.

## API Specifications

See `specs/api/` for detailed API schemas.

### Core APIs

1. **Orchestrator API**: Fleet management and coordination
2. **Agent Runtime API**: Planner/Worker/Judge interfaces
3. **Skills API**: Skill invocation and contract validation
4. **MCP Bridge API**: MCP server integration layer

## Database Schema

See `specs/database/` for ERD and schema definitions.

### Core Tables

- `agents`: Agent metadata and configuration
- `campaigns`: Campaign goals and state
- `tasks`: Task queue and execution state
- `content`: Generated content artifacts
- `engagements`: Social media interactions
- `transactions`: On-chain financial transactions

## Skill Contracts

See `specs/skills/` for Pydantic model definitions.

## System Interfaces

### MCP Integration

All external interactions MUST go through MCP servers. Direct API calls are prohibited.

### FastRender Swarm Pattern

- **Planner**: Task decomposition and planning
- **Worker**: Task execution (stateless, parallel)
- **Judge**: Quality assurance and state validation

## Validation

All specifications in this directory are validated using:

```bash
make spec-check
```

This ensures code alignment with specs before deployment.
