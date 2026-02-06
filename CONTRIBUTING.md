# Contributing to Project Chimera

Thank you for your interest in contributing to Project Chimera! This guide will help you understand our development process, coding standards, and how to submit contributions.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Branching Strategy](#branching-strategy)
- [Commit Conventions](#commit-conventions)
- [Pull Request Process](#pull-request-process)
- [Code Review Guidelines](#code-review-guidelines)
- [Spec-Driven Development](#spec-driven-development)
- [Testing Requirements](#testing-requirements)
- [Documentation Standards](#documentation-standards)

---

## Code of Conduct

Project Chimera follows a **Spec-Driven Development (SDD)** approach. This means:

- **Specs are the source of truth** - All code must align with specifications
- **Traceability is required** - All changes must reference relevant spec sections
- **Respect the Prime Directive** - Never generate code without checking `specs/` first

---

## Getting Started

### Prerequisites

- Python 3.12+
- Docker and Docker Compose
- Git
- Familiarity with the project structure (read `README.md` and `specs/_meta.md`)

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/habeneyasu/chimera-factory.git
cd chimera-factory

# Copy environment template
cp .env.example .env
# Edit .env with your configuration

# Install dependencies
make setup

# Start services
make docker-up

# Run tests to verify setup
make test
```

---

## Development Workflow

### The Prime Directive

**⚠️ NEVER generate code without checking `specs/` first.**

Before writing ANY code:
1. Read the relevant specifications in `specs/`
2. Understand the requirements from functional specs
3. Check the technical contracts (API schemas, data models)
4. Verify database schemas if working with data
5. Review skill contracts if implementing agent capabilities

### Standard Workflow

1. **Read Specs**: Check `specs/` directory for requirements
2. **Write Failing Tests**: Implement TDD by creating contract tests that define the 'empty slot' for the AI to fill
3. **Implement**: Code exactly what specs define
4. **Validate**: Run `make test` and verify spec alignment with full traceability
5. **Commit**: Include spec references in commit messages

---

## Branching Strategy

We use a **feature branch workflow** with the following branch types:

### Branch Types

- **`main`**: Production-ready code. Protected branch requiring PR reviews.
- **`develop`**: Integration branch for completed features. (Optional, currently using `main` directly)
- **`feature/*`**: New features or enhancements
- **`fix/*`**: Bug fixes
- **`docs/*`**: Documentation updates
- **`refactor/*`**: Code refactoring without changing functionality
- **`test/*`**: Test improvements or additions

### Branch Naming Convention

```
<type>/<short-description>

Examples:
- feature/trend-research-reddit
- fix/rate-limit-handling
- docs/api-documentation
- refactor/skill-interface
- test/integration-coverage
```

### Creating a Branch

```bash
# Update main branch
git checkout main
git pull origin main

# Create and switch to feature branch
git checkout -b feature/your-feature-name

# Or use the shorthand
git checkout -b feature/your-feature-name origin/main
```

---

## Commit Conventions

We follow the **Conventional Commits** specification for clear, traceable commit messages.

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Commit Types

- **`feat`**: New feature
- **`fix`**: Bug fix
- **`docs`**: Documentation changes
- **`style`**: Code style changes (formatting, no logic change)
- **`refactor`**: Code refactoring
- **`test`**: Adding or updating tests
- **`chore`**: Maintenance tasks (dependencies, build config)
- **`perf`**: Performance improvements
- **`ci`**: CI/CD changes

### Scope (Optional)

- `api`: API routes or endpoints
- `skills`: Agent skills
- `db`: Database changes
- `specs`: Specification updates
- `docker`: Docker configuration
- `tests`: Test suite

### Examples

```bash
# Feature with spec reference
feat(skills): add Reddit trend research
Ref: specs/functional.md US-003
Ref: specs/technical.md section 2.3

# Bug fix
fix(api): handle rate limit errors gracefully
Ref: specs/technical.md section 1.5

# Documentation
docs(readme): update architecture diagram

# Test addition
test(integration): add skill workflow tests
Ref: specs/functional.md US-001 acceptance criteria

# Spec update (must come before implementation)
docs(specs): add user story for engagement scheduling
Ref: specs/functional.md US-010
```

### Commit Message Best Practices

1. **Reference Specs**: Always include `Ref: specs/...` in the body
2. **Be Descriptive**: Subject line should be clear and concise (50 chars or less)
3. **Explain Why**: Body should explain the change and rationale
4. **Link Issues**: Use `Closes #123` or `Fixes #123` in footer if applicable
5. **One Logical Change**: Each commit should represent one logical change

### Bad Commit Messages

```bash
# ❌ Too vague
git commit -m "fix bug"

# ❌ No spec reference
git commit -m "feat: add new skill"

# ❌ Multiple unrelated changes
git commit -m "fix api and update docs"
```

### Good Commit Messages

```bash
# ✅ Clear, specific, with spec reference
git commit -m "feat(skills): implement Reddit trend research

Add RedditClient to fetch trending posts from subreddits.
Implements parallel trend aggregation across multiple sources.

Ref: specs/functional.md US-003
Ref: specs/technical.md section 2.3
Ref: specs/skills/skill_trend_research/contract.json

Closes #45"
```

---

## Pull Request Process

### Before Submitting

1. **Update Specs First** (if needed): If your change requires spec updates, update `specs/` first
2. **Write Tests**: Ensure all new code has tests (minimum 80% coverage)
3. **Run Tests Locally**: `make test` must pass
4. **Check Linting**: `ruff check` and `mypy` must pass
5. **Update Documentation**: Update relevant docs if APIs or behavior changed
6. **Rebase on Main**: Ensure your branch is up-to-date with `main`

### PR Title Format

Follow the same convention as commit messages:

```
<type>(<scope>): <subject>
```

### PR Description Template

```markdown
## Description
Brief description of the change.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update
- [ ] Refactoring

## Spec References
- Ref: specs/functional.md US-XXX
- Ref: specs/technical.md section X.Y
- Ref: specs/... (if applicable)

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] All tests pass locally
- [ ] Test coverage maintained (≥80%)

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Specs updated (if needed)
- [ ] Tests added/updated
- [ ] All tests pass

## Related Issues
Closes #123
```

### PR Review Requirements

- **Minimum 1 approval** required before merging
- **All CI checks must pass** (tests, linting, type checking)
- **Spec alignment verified** by reviewer
- **No merge conflicts** with `main`

### After PR Approval

1. **Squash and Merge**: Use "Squash and Merge" to keep history clean
2. **Delete Branch**: Delete the feature branch after merge
3. **Update Local**: `git checkout main && git pull origin main`

---

## Code Review Guidelines

### For Authors

- **Be Responsive**: Respond to review comments promptly
- **Be Open**: Accept constructive feedback gracefully
- **Explain Decisions**: If you disagree, explain your reasoning
- **Update PR**: Push fixes as new commits (we'll squash on merge)

### For Reviewers

- **Be Constructive**: Provide actionable feedback
- **Check Spec Alignment**: Verify code matches specifications
- **Verify Tests**: Ensure adequate test coverage
- **Check Traceability**: Verify spec references are present
- **Be Timely**: Review within 48 hours when possible

### Review Checklist

- [ ] Code aligns with specifications
- [ ] Spec references are present in commits/docs
- [ ] Tests are adequate and passing
- [ ] Code follows style guidelines (type hints, Pydantic models)
- [ ] Error handling is appropriate
- [ ] Documentation is updated
- [ ] No security concerns
- [ ] Performance considerations addressed (if applicable)

---

## Spec-Driven Development

### When to Update Specs

**Update specs BEFORE code** if:
- Adding a new feature
- Changing API contracts
- Modifying database schema
- Adding new skills
- Changing behavior

**Update specs AFTER code** if:
- Fixing a bug that reveals a spec gap
- Clarifying ambiguous requirements

### Spec Update Process

1. **Create spec PR first** (if major change)
2. **Get spec approval** from maintainers
3. **Implement according to spec**
4. **Verify alignment** with `make spec-check`

### Spec File Locations

- `specs/_meta.md`: Master specification
- `specs/functional.md`: User stories and requirements
- `specs/technical.md`: API contracts and data models
- `specs/openclaw_integration.md`: Network integration
- `specs/database/schema.sql`: Database schema
- `skills/skill_*/contract.json`: Skill contracts

---

## Testing Requirements

### Test Types

1. **Contract Tests**: Verify skill interfaces match contracts
2. **Unit Tests**: Test individual functions/classes
3. **Integration Tests**: Test component interactions
4. **E2E Tests**: Test complete workflows

### Test Coverage

- **Minimum 80% coverage** for all production code
- **100% coverage** for critical paths (API routes, skills, error handling)

### Running Tests

```bash
# Run all tests
make test

# Run specific test suite
pytest tests/unit/
pytest tests/integration/
pytest tests/contracts/

# Run with coverage
pytest --cov=src/chimera_factory tests/

# Run specific test file
pytest tests/integration/test_api.py
```

### Writing Tests

- **Follow TDD**: Write failing tests first
- **Use descriptive names**: `test_skill_handles_rate_limit_error`
- **Test edge cases**: Empty inputs, error conditions, boundary values
- **Mock external APIs**: Don't make real API calls in tests
- **Reference specs**: Include spec references in test docstrings

---

## Documentation Standards

### Code Documentation

- **Docstrings**: All public functions/classes must have docstrings
- **Type Hints**: All functions must have type annotations
- **Spec References**: Include references to relevant spec sections

Example:
```python
def research_trends(
    topic: str,
    sources: List[str],
    timeframe: str = "24h"
) -> List[TrendItem]:
    """
    Research trends from multiple sources.
    
    Args:
        topic: Topic or keyword to research
        sources: List of sources to query (twitter, news, reddit)
        timeframe: Time window for trend analysis (1h, 24h, 7d, 30d)
    
    Returns:
        List of trend items with metadata
    
    Raises:
        SkillError: If trend research fails
    
    See Also:
        specs/functional.md US-001: Research Trends from Multiple Sources
        specs/technical.md section 1: Trend Research API
    """
    pass
```

### Documentation Updates

When updating:
- **API Documentation**: Update `docs/API.md` if endpoints change
- **Docker Guide**: Update `docs/DOCKER.md` if Docker config changes
- **README**: Update `README.md` for major feature additions
- **ADRs**: Create ADR for significant architectural decisions

---

## Getting Help

- **Read First**: Check `README.md`, `specs/_meta.md`, and `.cursor/rules`
- **Search Issues**: Check existing GitHub issues
- **Ask Questions**: Open a discussion or issue with the `question` label
- **Review Examples**: Look at existing code and PRs for patterns

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to Project Chimera!** 🏭
