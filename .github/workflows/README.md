# CI/CD Pipeline Documentation

## Overview

This directory contains GitHub Actions workflows for Project Chimera's CI/CD pipeline.

## Workflows

### `main.yml` - Primary CI/CD Pipeline

Runs on every push and pull request to `main`, `develop`, and `task-*` branches.

**Jobs:**

1. **Spec Validation** (`spec-check`)
   - Validates spec directory structure
   - Checks required spec files
   - Verifies skill contracts
   - Validates database schema

2. **Code Linting** (`lint`)
   - Runs `ruff` for code style checks
   - Runs `mypy` for type checking
   - Ensures code quality standards

3. **Tests** (`test`)
   - Builds Docker image
   - Runs `make test` (executes tests in Docker)
   - Note: Tests are expected to fail until implementations are added (TDD approach)

4. **Security Scan** (`security`)
   - Checks for hardcoded secrets
   - Scans for potential security vulnerabilities
   - Validates dependency security

5. **Build Verification** (`build`)
   - Verifies Dockerfile builds successfully
   - Validates docker-compose configuration

6. **CI Summary** (`ci-summary`)
   - Provides summary of all job results
   - Runs after all other jobs complete

## Integration with CodeRabbit

CodeRabbit AI reviews are configured via `.coderabbit.yaml` in the repository root. CodeRabbit:
- Reviews PRs automatically
- Checks spec alignment
- Validates security
- Enforces Spec-Driven Development principles

## Local Testing

To test the CI pipeline locally:

```bash
# Run spec-check
make spec-check

# Run tests (requires Docker)
make test

# Run linting
uv run ruff check .
uv run mypy src/ tests/
```

## Workflow Status Badge

Add this to your README.md:

```markdown
[![CI/CD Pipeline](https://github.com/habeneyasu/chimera-factory/actions/workflows/main.yml/badge.svg)](https://github.com/habeneyasu/chimera-factory/actions/workflows/main.yml)
```
