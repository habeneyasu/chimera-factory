> **AI Agents**: Read `.cursor/rules` first. This repository follows Spec-Driven Development - implementation code must align with `specs/` directory.

# 🏭 Project Chimera: The Autonomous Influencer Factory

**Build digital influencers that research trends, generate content, and manage engagement—autonomously.**

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![Spec-Driven](https://img.shields.io/badge/Spec--Driven-Development-orange)](specs/_meta.md)
[![TDD Ready](https://img.shields.io/badge/TDD-Failing%20Tests-red)](tests/)
[![MCP x3](https://img.shields.io/badge/MCP-3%20servers-green)](.cursor/mcp.json)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](Dockerfile)
[![CI/CD](https://github.com/habeneyasu/chimera-factory/actions/workflows/main.yml/badge.svg)](https://github.com/habeneyasu/chimera-factory/actions)
[![CodeRabbit](https://img.shields.io/badge/CodeRabbit-Review-blue)](.coderabbit.yaml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ❌ The Problem

Most AI projects fail because they:
- Rely on fragile prompts that break at scale
- Have messy, unmaintainable codebases
- Hallucinate when specifications are ambiguous
- Lack traceability and governance

## ✅ The Solution

Project Chimera is a **factory** for autonomous AI influencers:
- **Spec-Driven Development**: Intent is the source of truth
- **Agentic Orchestration**: Hierarchical swarm architecture (Planner-Worker-Judge)
- **Governance First**: CI/CD, Docker, failing tests ensure reliability
- **Network Integration**: Active participation in OpenClaw agent social network
- **Human-in-the-Loop**: Confidence-based escalation for safety

**This isn't another chatbot. This is a factory architected so that a swarm of AI agents can build features with minimal human conflict.**

---

## 🏗️ Architecture

### Agent Pattern: FastRender Swarm

```mermaid
graph TD
    H[Human Orchestrator] --> P[Planner Agent]
    P --> W1[Worker 1: Research]
    P --> W2[Worker 2: Generate]
    P --> W3[Worker 3: Engage]
    W1 --> J[Judge Agent]
    W2 --> J
    W3 --> J
    J -->|Confidence > 0.9| A[Auto-Approve]
    J -->|Confidence 0.7-0.9| Q[HITL Queue]
    J -->|Confidence < 0.7| R[Reject/Retry]
    Q --> HR[Human Review]
    HR --> A
```

**Hybrid Database Strategy**:
- **Weaviate**: Semantic memory for AI (vector database, RAG)
- **PostgreSQL**: Transactional data (campaigns, approvals, audit logs)
- **Redis**: Ephemeral cache & task queues
- **On-Chain**: Financial ledger (Agentic Commerce)

---

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/habeneyasu/chimera-factory
cd chimera-factory

# Install dependencies
make setup

# Run tests (Docker-based)
make test

# Validate specifications
make spec-check

# Verify MCP integration
make verify-mcp
# Or see docs/MCP_INTEGRATION.md for detailed setup
```

**Prerequisites**:
- Python 3.12+
- Node.js and npx (for MCP servers)
- Docker and Docker Compose
- Cursor IDE (or compatible MCP client)

---

## 📁 Repository Structure

```
chimera-factory/
├── .cursor/              # IDE configuration and AI co-pilot rules
│   ├── rules            # Prime Directive: "NEVER code without checking specs/"
│   └── mcp.json         # MCP server configuration
├── docs/                 # Documentation
│   ├── MCP_INTEGRATION.md
│   └── mcp.json.example
├── research/             # Research findings and architecture strategy
│   ├── architecture_strategy.md
│   ├── tooling_strategy.md
│   └── submission_report_feb4.md
├── specs/                # Specifications (SDD source of truth)
│   ├── _meta.md         # Master specification
│   ├── functional.md    # Comprehensive user stories for agentic workflows
│   ├── technical.md     # API contracts and data models
│   ├── openclaw_integration.md
│   ├── api/             # OpenAPI specifications
│   ├── database/        # Database schemas and ERD
│   └── skills/          # Skill contract definitions
├── skills/               # Agent runtime capabilities
│   ├── skill_trend_research/
│   │   ├── README.md     # Contract: Input/Output
│   │   ├── contract.json # JSON Schema validation
│   │   └── __init__.py   # Pydantic models (from specs/skills/)
│   ├── skill_content_generate/
│   │   └── ... (same structure)
│   └── skill_engagement_manage/
│       └── ... (same structure)
├── src/                  # Python package (SDD-compliant)
│   └── chimera_factory/
├── tests/                # Test suite (TDD approach)
└── pyproject.toml        # Project configuration
```

---

## 🤖 For AI Agents

**Prime Directive**: **ALWAYS check `specs/` before writing code.**

### 1. Read These First:
- `specs/_meta.md` - Project vision and constraints
- `specs/functional.md` - User stories and acceptance criteria
- `specs/technical.md` - API contracts and data models
- `.cursor/rules` - Development rules and patterns

### 2. Follow Spec-Driven Development:
- **NEVER** write code without checking specs first
- **ALWAYS** explain your plan before implementation
- **REFERENCE** spec sections in code comments
- **VALIDATE** with `make spec-check` before committing

### 3. Traceability:
- MCP Sense tracks all changes (Tenx integration)
- Commit messages must reference spec sections
- All actions logged for audit trail

**See `.cursor/rules` for complete AI co-pilot guidelines.**

---

## 🧪 TDD Approach: Failing Tests Define Success

We practice **True Test-Driven Development**:

```python
# Example from tests/test_trend_research.py
def test_trend_research_returns_correct_structure():
    # This test FAILS intentionally - it defines the contract
    result = research_trends(topic="AI influencers", sources=["twitter", "news"])
    assert isinstance(result, dict)
    assert "trends" in result
    assert "confidence" in result
    assert isinstance(result["trends"], list)
    # Implementation doesn't exist yet - that's the point!
```

**Why Failing Tests?**: They create "empty slots" that AI agents must fill with correct implementations. Tests define the contract before code exists.

---

## 🔄 Development Workflow

```mermaid
graph LR
    A[Read Specs] --> B[Write Failing Tests]
    B --> C[Implement Feature]
    C --> D[Run Tests]
    D --> E{All Tests Pass?}
    E -->|Yes| F[Commit with Context]
    E -->|No| C
    F --> G[Push → CI/CD Runs]
    G --> H[Spec Validation]
```

**Workflow Steps**:
1. **Check Specs**: Read relevant specifications in `specs/`
2. **Plan Implementation**: Explain approach with spec references
3. **Write Tests**: Create tests based on acceptance criteria (TDD)
4. **Implement**: Code exactly what specs define
5. **Validate**: Run `make spec-check` and `make test`
6. **Commit**: Include spec references in commit messages

---

## ✨ Key Features

| Feature | Description | Status |
|---------|-------------|--------|
| **Spec-Driven Dev** | Intent as source of truth | ✅ Implemented |
| **MCP Integration** | Universal tool interface (3 dev servers) | ✅ Connected |
| **FastRender Swarm** | Planner-Worker-Judge pattern | 📋 Spec Complete |
| **Agent Skills** | Modular capabilities (3 critical skills) | 📋 Contract Defined |
| **OpenClaw Network** | Agent social protocols | 📋 Spec Complete |
| **Human-in-the-Loop** | Confidence-based approval workflow | 📋 Spec Complete |
| **Hybrid Database** | PostgreSQL + Weaviate (Vector) + Redis + On-Chain | 📋 Schema Defined |
| **Docker Testing** | Containerized test environment | ✅ Implemented |

---

## 🌟 The Chimera Difference

| Traditional AI Projects | Project Chimera |
|------------------------|-----------------|
| Build the product | Build the **factory** |
| Prompts as "code" | Specs as source of truth |
| Manual testing | **Failing tests define success** |
| "It works on my machine" | Dockerized from day 1 |
| AI as assistant | **AI as primary builder** |
| Human writes code | Human writes specs, AI implements |

### Why This Isn't Another AI Project

1. **We're building the factory, not the product**
   - Infrastructure enables autonomous agent development
   - Specs define intent, agents implement features

2. **AI agents can build the final features**
   - Repository architected for swarm development
   - Clear boundaries between development tools and runtime capabilities

3. **Every decision is spec-ratified**
   - No code without specifications
   - Traceability from spec to implementation

4. **Full traceability via MCP Sense**
   - "Black box" recording of all development activities
   - Complete audit trail for governance

5. **Network-first architecture**
   - Agents participate in OpenClaw social network
   - Discover, collaborate, and share with other agents

---

## 📊 Project Status

**Task 1 - The Strategist** ✅ **COMPLETE**
- [x] Environment setup and Git repository initialization
- [x] Research and reading (SRS, OpenClaw, MoltBook, a16z)
- [x] Architecture strategy documentation
- [x] MCP integration and verification
- [x] Submission report

**Task 2 - The Architect** ✅ **COMPLETE**
- [x] **Task 2.1**: Master Specification
  - [x] `specs/_meta.md` - High-level vision and constraints
  - [x] `specs/functional.md` - Comprehensive user stories from agent perspective
  - [x] `specs/technical.md` - API contracts and data models
  - [x] `specs/database/schema.sql` - Database schema with video metadata
  - [x] `specs/database/erd.md` - Entity Relationship Diagram
  - [x] `specs/openclaw_integration.md` - Network integration plan
- [x] **Task 2.2**: Context Engineering & "The Brain"
  - [x] `.cursor/rules` - AI co-pilot rules with Prime Directive
- [x] **Task 2.3**: Tooling & Skills Strategy
  - [x] `research/tooling_strategy.md` - Developer tools (MCP) documentation
  - [x] `skills/README.md` - Agent skills overview
  - [x] `skills/skill_trend_research/README.md` - Trend research skill (Input/Output contracts defined)
  - [x] `skills/skill_content_generate/README.md` - Content generation skill (Input/Output contracts defined)
  - [x] `skills/skill_engagement_manage/README.md` - Engagement management skill (Input/Output contracts defined)

**Task 3 - The Governor** 🟡 **IN PROGRESS**
- [x] **Task 3.1**: Test-Driven Development
  - [x] `tests/test_init.py` - Basic package tests
  - [ ] `tests/test_trend_research.py` - Trend data structure tests
  - [ ] `tests/test_skills_interface.py` - Skills contract tests
  - [ ] `tests/test_openclaw_integration.py` - Network protocol tests
- [x] **Task 3.2**: Containerization & Automation
  - [x] `Dockerfile` - Environment containerization ✅
  - [x] `Makefile` - Standardized commands ✅
  - [x] `docker-compose.yml` - Multi-service setup ✅
  - [ ] `make spec-check` script - Spec validation
- [ ] **Task 3.3**: CI/CD & AI Governance
  - [ ] `.github/workflows/main.yml` - GitHub Actions
  - [ ] `.coderabbit.yaml` - AI review policy
  - [ ] CodeRabbit/ReviewDog integration

---

## 📚 Documentation

### Core Documentation
- **Master Specification**: `specs/_meta.md` - Project vision and constraints
- **Functional Specs**: `specs/functional.md` - Comprehensive user stories for agentic workflows
- **Technical Specs**: `specs/technical.md` - API contracts and data models
- **Database Schema**: `specs/database/schema.sql` - Complete schema with video metadata
- **OpenClaw Integration**: `specs/openclaw_integration.md` - Network participation plan

### Architecture & Research
- **Architecture Strategy**: `research/architecture_strategy.md`
- **Tooling Strategy**: `research/tooling_strategy.md` - MCP vs Skills separation
- **Research Notes**: `research/research_notes.md`
- **Submission Report**: `research/submission_report_feb4.md`

### Development Guides
- **MCP Integration**: `docs/MCP_INTEGRATION.md` - Setup and verification
- **AI Co-Pilot Rules**: `.cursor/rules` - Development guidelines
- **Skills Documentation**: `skills/README.md` - Agent capabilities

---

## 🤝 Contributing

This project follows **Spec-Driven Development (SDD)**:

1. **NEVER** write code without checking `specs/` first
2. **ALWAYS** write failing tests before implementation (TDD)
3. **COMMIT** early and often with descriptive messages
4. **REFERENCE** spec sections in code comments

### Development Commands:
```bash
make setup      # Install dependencies
make test       # Run tests in Docker
make spec-check # Validate spec alignment
make verify-mcp # Verify MCP server connections
make clean      # Clean build artifacts
```

---

## 🔗 Links

- **Repository**: [https://github.com/habeneyasu/chimera-factory](https://github.com/habeneyasu/chimera-factory)
- **Specifications**: `specs/` directory
- **MCP Integration**: `docs/MCP_INTEGRATION.md`
- **Model Context Protocol**: https://modelcontextprotocol.io
- **MCP Server Registry**: https://github.com/modelcontextprotocol/servers

---

## 🎥 Final Deliverables (Due Friday)

1. **Complete Repository** with:
   - ✅ `specs/` directory (comprehensive user stories, API contracts, database schema)
   - ✅ `tests/` directory (failing tests defining implementation targets)
   - ✅ `skills/` directory (3+ skill contracts with Pydantic models)
   - ✅ `Dockerfile` & `Makefile` (containerized environment)
   - [ ] `.github/workflows/` (CI/CD pipeline)
   - ✅ `.cursor/rules` (AI co-pilot prime directive)

2. **5-Minute Loom Video** demonstrating:
   - Spec structure and SDD principles
   - Failing tests running (TDD approach)
   - IDE agent understanding project context
   - MCP Sense telemetry verification

3. **MCP Telemetry Active** throughout development

---

## 📄 License

See LICENSE file for details.
