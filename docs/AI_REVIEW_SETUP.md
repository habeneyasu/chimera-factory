# AI Review & Governance Pipeline Setup

This document describes the AI review configuration and governance pipeline for Project Chimera.

## Overview

Project Chimera uses a multi-layered AI review and governance system:

1. **CodeRabbit AI Reviews**: Automated code reviews via GitHub App
2. **GitHub Actions Validation**: Automated spec alignment and security checks
3. **Manual Review**: Human reviewers verify AI recommendations

---

## CodeRabbit Configuration

### Setup Instructions

1. **Install CodeRabbit GitHub App**
   - Visit: https://github.com/apps/coderabbitai
   - Click "Install" and select your repository
   - Grant necessary permissions

2. **Configuration File**
   - CodeRabbit reads `.coderabbit.yaml` from the repository root
   - Configuration includes:
     - Review types (code quality, security, performance)
     - Custom instructions for SDD enforcement
     - Path inclusions/exclusions
     - Language-specific settings

3. **Automatic Reviews**
   - CodeRabbit automatically reviews all pull requests
   - Reviews include inline comments and summary
   - Reviews run before CI completes (faster feedback)

### Configuration Details

The `.coderabbit.yaml` file configures:

- **Spec-Driven Development (SDD) Enforcement**
  - Requires spec references in PR descriptions
  - Validates API contract alignment
  - Checks database schema compliance
  - Verifies skill contract implementation

- **Security Checks**
  - Detects hardcoded secrets
  - Validates MCP usage (no direct API calls)
  - Checks dependency injection patterns
  - Flags security anti-patterns

- **Code Quality Standards**
  - Requires type hints
  - Prefers Pydantic models
  - Checks docstring quality
  - Validates error handling

- **Architecture Pattern Compliance**
  - FastRender Swarm pattern (Planner-Worker-Judge)
  - Hybrid database architecture (Weaviate, PostgreSQL, Redis)
  - MCP for external interactions
  - Dependency injection for skills

---

## GitHub Actions AI Review Workflow

### Workflow: `ai-review.yml`

Runs on every pull request and provides:

1. **Spec Alignment Validation**
   - Checks PR description for spec references
   - Validates code comments reference specs/
   - Verifies API contract alignment
   - Runs `make spec-check`

2. **Enhanced Security Scanning**
   - Bandit security scan
   - Secrets detection (hardcoded passwords, API keys)
   - Safety dependency vulnerability check
   - Pattern-based secret detection

3. **Code Quality Checks**
   - Type hint validation
   - Ruff linting
   - MyPy type checking
   - Code quality standards compliance

### Integration with Main CI Pipeline

The main CI pipeline (`.github/workflows/main.yml`) includes:

- **AI Review Integration Job**: Provides status summary
- **Parallel Execution**: AI review runs alongside other CI jobs
- **Summary Reports**: Consolidated results in CI summary

---

## Review Checklist

### For Authors

Before submitting a PR, ensure:

- [ ] PR description includes spec references (`Ref: specs/...`)
- [ ] Code comments reference relevant spec sections
- [ ] API routes match `specs/technical.md` contracts
- [ ] Database changes align with `specs/database/schema.sql`
- [ ] Skill implementations match `skills/skill_*/contract.json`
- [ ] No hardcoded secrets (use environment variables)
- [ ] MCP is used for external interactions
- [ ] Dependency injection is used (no direct DB connections)
- [ ] Type hints are present on all functions
- [ ] Tests reference specs in docstrings

### For Reviewers

When reviewing PRs:

1. **Check CodeRabbit Comments**
   - Review inline comments on code
   - Check summary comment for overall assessment
   - Address high-confidence recommendations

2. **Verify Spec Alignment**
   - Confirm PR description references specs
   - Check that code matches spec requirements
   - Validate API contracts are followed

3. **Security Review**
   - Verify no secrets in code
   - Check MCP usage for external APIs
   - Validate dependency injection patterns

4. **Code Quality**
   - Ensure type hints are present
   - Verify Pydantic models are used
   - Check error handling is appropriate

---

## Custom Instructions

CodeRabbit uses custom instructions from `.coderabbit.yaml` to enforce:

### Prime Directive Enforcement

⚠️ **NEVER approve code without checking specs/ first.**

CodeRabbit is instructed to:
- Verify spec references in PR descriptions
- Check code alignment with specifications
- Validate API contract compliance
- Ensure database schema alignment

### Spec Alignment Checks

- **API Routes**: Match OpenAPI spec in `specs/technical.md`
- **Skills**: Match contracts in `skills/skill_*/contract.json`
- **Database**: Match schema in `specs/database/schema.sql`
- **Models**: Use Pydantic models from `specs/skills/__init__.py`

### Security Checks

- **Secrets Management**: Flag hardcoded secrets
- **MCP Usage**: Verify all external interactions use MCP
- **Dependency Injection**: Check skills use injection pattern

### Architecture Patterns

- **FastRender Swarm**: Planner-Worker-Judge pattern
- **Database Architecture**: Weaviate (memory), PostgreSQL (transactions), Redis (cache)
- **MCP Protocol**: All external interactions via MCP

---

## Troubleshooting

### CodeRabbit Not Reviewing PRs

1. **Check GitHub App Installation**
   - Verify CodeRabbit app is installed
   - Check repository permissions
   - Ensure app is enabled for the repository

2. **Verify Configuration**
   - Check `.coderabbit.yaml` exists
   - Validate YAML syntax
   - Ensure configuration is correct

3. **Check App Status**
   - Visit repository settings → Integrations → CodeRabbit
   - Verify app is active
   - Check for error messages

### GitHub Actions Workflow Issues

1. **Workflow Not Running**
   - Check workflow file exists: `.github/workflows/ai-review.yml`
   - Verify trigger conditions (pull_request events)
   - Check repository Actions settings

2. **Job Failures**
   - Review job logs in Actions tab
   - Check for dependency issues
   - Verify Python version compatibility

### Spec Alignment Failures

1. **Missing Spec References**
   - Add `Ref: specs/...` to PR description
   - Include spec references in code comments
   - Update `.cursor/rules` if needed

2. **API Contract Mismatches**
   - Review `specs/technical.md` for correct contracts
   - Update code to match specs
   - Or update specs if requirements changed

---

## Best Practices

### For Development

1. **Write Specs First**: Update `specs/` before implementing code
2. **Reference Specs**: Always include `Ref: specs/...` in commits and PRs
3. **Follow Patterns**: Use established architecture patterns
4. **Use Type Hints**: Add type hints to all functions
5. **Test Coverage**: Maintain ≥80% test coverage

### For Code Review

1. **Trust AI Recommendations**: CodeRabbit catches many issues early
2. **Verify Spec Alignment**: Always check spec references
3. **Security First**: Prioritize security-related comments
4. **Architecture Compliance**: Ensure patterns are followed
5. **Documentation**: Verify docstrings and comments

---

## Configuration Files

- **`.coderabbit.yaml`**: CodeRabbit AI review configuration
- **`.github/workflows/ai-review.yml`**: GitHub Actions AI review workflow
- **`.github/workflows/main.yml`**: Main CI/CD pipeline (includes AI review integration)
- **`.cursor/rules`**: AI co-pilot rules (used by IDE agents)

---

## References

- **CodeRabbit Documentation**: https://docs.coderabbit.ai
- **GitHub Actions**: https://docs.github.com/en/actions
- **Spec-Driven Development**: `specs/_meta.md`
- **Contributing Guide**: `CONTRIBUTING.md`
- **Architecture Decision Records**: `docs/adr/`

---

**Last Updated**: 2026-02-06  
**Maintained By**: habeneyasu
