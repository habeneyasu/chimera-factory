# Project Chimera: The Agentic Infrastructure Challenge

**Repository**: [https://github.com/habeneyasu/chimera-factory](https://github.com/habeneyasu/chimera-factory)

## Overview

Project Chimera is a factory for building autonomous AI influencers—digital entities that research trends, generate content, and manage engagement without human intervention. This repository implements the infrastructure following Spec-Driven Development (SDD) principles.

## Core Principles

- **Spec-Driven Development (SDD)**: Specifications are the source of truth
- **Traceability**: Tenx MCP Sense connected for development telemetry
- **Agentic Architecture**: FastRender Swarm pattern (Planner-Worker-Judge)
- **Model Context Protocol (MCP)**: Universal interface for external interactions
- **Human-in-the-Loop (HITL)**: Confidence-based escalation for safety

## Repository Structure

```
chimera-factory/
├── .cursor/              # IDE configuration and MCP setup
├── docs/                 # Documentation
├── research/             # Research findings and architecture strategy
├── specs/                # Specifications (SDD source of truth)
├── skills/               # Agent runtime capabilities
├── src/                  # Python package (SDD-compliant)
├── tests/                # Test suite
└── pyproject.toml        # Project configuration
```

## Development Status

**Day 1 (February 4, 2026)**: Task 1 - The Strategist ✅ **COMPLETE**
- [x] Environment setup and Git repository initialization
- [x] Research and reading (SRS, OpenClaw, MoltBook, a16z)
- [x] Architecture strategy documentation
- [x] MCP integration and verification
- [x] Submission report

## Quick Start

```bash
# Setup Python environment
make setup

# Run tests
make test

# Verify MCP integration
# See docs/MCP_INTEGRATION.md
```

## Documentation

- **Architecture**: `research/architecture_strategy.md`
- **MCP Integration**: `docs/MCP_INTEGRATION.md`
- **Research Findings**: `research/research_notes.md`
- **Submission Report**: `research/submission_report_feb4.md`
- **Tooling Strategy**: `research/tooling_strategy.md`

## Requirements

- Python 3.12+
- Node.js and npx (for MCP servers)
- Cursor IDE (or compatible MCP client)
- Tenx MCP Sense (for traceability)

## License

See LICENSE file for details.
