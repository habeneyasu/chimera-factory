# Project Chimera: The Agentic Infrastructure Challenge

## Mission
Architect the "Factory" that builds the "Autonomous Influencer" - digital entities that research trends, generate content, and manage engagement without human intervention.

## Core Philosophies

- **Spec-Driven Development (SDD)**: Intent (Specs) is the source of truth
- **Traceability (MCP)**: Tenx MCP Sense server connected for "Black Box" flight recorder
- **Agentic "Skills" vs. "Tools"**: Clear separation between Skills (reusable functions) and MCP Servers (external bridges)
- **Git Hygiene**: Commit early, commit often (Minimum 2x/day)

## Repository Structure

```
chimera-factory/
├── specs/              # GitHub Spec Kit structure
├── research/           # Research notes and architecture strategy
├── skills/             # Agent Skills (runtime capabilities)
├── tests/              # Test-driven development tests
├── .cursor/            # IDE context and rules
└── .github/workflows/  # CI/CD pipelines
```

## Development Status

**Day 1 (February 4, 2025)**: Task 1 - The Strategist
- [x] Environment Setup
- [ ] Research & Reading
- [ ] Architecture Strategy

## Getting Started

```bash
# Setup environment
make setup

# Run tests
make test

# Check spec alignment
make spec-check
```

## MCP Telemetry

This project requires Tenx MCP Sense to be connected to the IDE at all times for traceability and governance.
