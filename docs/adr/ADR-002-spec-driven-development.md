# ADR-002: Spec-Driven Development (SDD) Approach

**Status**: Accepted  
**Date**: 2026-02-06  
**Deciders**: Architecture Team  
**Tags**: architecture, methodology, sdd, specifications, traceability

---

## Context

Traditional software development approaches face challenges when AI agents are primary contributors:

1. **Prompt Fragility**: AI-generated code based on prompts is brittle and inconsistent
2. **Lack of Traceability**: No clear link between requirements and implementation
3. **Spec-Implementation Drift**: Specifications and code diverge over time
4. **AI Agent Confusion**: AI agents struggle to understand project context without clear specifications
5. **Quality Assurance**: Difficult to verify that implementations match intended behavior

Project Chimera requires a methodology that:
- Enables AI agents to build features autonomously
- Maintains consistency between requirements and code
- Provides clear traceability for all changes
- Supports automated validation of spec alignment

---

## Decision

We will adopt **Spec-Driven Development (SDD)** as the core development methodology, where:

1. **Specifications are the source of truth** - All implementation decisions must align with `specs/` directory
2. **Prime Directive**: "NEVER generate code without checking specs/ first"
3. **Traceability Required**: All code changes must reference relevant spec sections
4. **Specs First**: Specifications are updated before code (except for bug fixes that reveal spec gaps)
5. **Executable Specs**: Specifications are machine-readable (Pydantic models, JSON Schema, OpenAPI)

---

## Alternatives Considered

### Alternative 1: Traditional Agile/Scrum with User Stories

**Approach**: Use standard Agile methodology with user stories in a backlog, implemented by developers or AI agents.

**Pros**:
- Well-established methodology
- Familiar to most developers
- Flexible and adaptable

**Cons**:
- **No Machine-Readable Format**: User stories are narrative text, not executable
- **AI Agent Confusion**: AI agents struggle to parse narrative requirements
- **Spec Drift**: No mechanism to prevent code from diverging from stories
- **No Validation**: Cannot automatically verify that code matches stories
- **Lack of Traceability**: Difficult to link code changes to specific story requirements

**Rejected Because**: Does not provide the structure and traceability needed for AI agents to work autonomously and maintain consistency.

---

### Alternative 2: Test-Driven Development (TDD) Only

**Approach**: Write tests first, then implement code to pass tests.

**Pros**:
- Tests serve as executable specifications
- Ensures code meets requirements
- Good for regression prevention

**Cons**:
- **Tests as Specs**: Tests describe "how" but not "why" or high-level intent
- **No High-Level Design**: Lacks architectural guidance and system boundaries
- **AI Agent Limitations**: AI agents need structured specifications, not just test cases
- **No Contract Definition**: Tests don't define API contracts or data models explicitly

**Rejected Because**: Tests alone are insufficient. We need structured specifications that define intent, architecture, and contracts before tests are written.

---

### Alternative 3: API-First Development

**Approach**: Define APIs first (OpenAPI/Swagger), then implement.

**Pros**:
- Clear API contracts
- Machine-readable specifications
- Good for API design

**Cons**:
- **Limited Scope**: Only covers API layer, not business logic, database schema, or agent behavior
- **No Functional Specs**: Doesn't capture user stories or acceptance criteria
- **No Architectural Guidance**: Doesn't define system architecture or patterns
- **Incomplete for Agents**: AI agents need more than API contracts

**Rejected Because**: Too narrow in scope. We need comprehensive specifications covering functional requirements, technical contracts, architecture, and agent behavior.

---

### Alternative 4: Behavior-Driven Development (BDD)

**Approach**: Write specifications in natural language (Gherkin), then implement.

**Pros**:
- Human-readable specifications
- Executable via test frameworks (Cucumber, Behave)
- Good for collaboration

**Cons**:
- **Natural Language Ambiguity**: AI agents struggle with ambiguous natural language
- **Limited Technical Detail**: Doesn't capture API contracts, data models, or architecture
- **No Machine-Readable Contracts**: Gherkin doesn't define JSON schemas or type systems
- **Maintenance Overhead**: Natural language specs require constant interpretation

**Rejected Because**: Natural language specifications are too ambiguous for AI agents and lack the technical precision needed for implementation.

---

## Consequences

### Positive

1. **AI Agent Autonomy**: AI agents can work independently by reading structured specifications
   - Clear requirements in `specs/functional.md`
   - Technical contracts in `specs/technical.md`
   - Architecture guidance in `specs/_meta.md`

2. **Traceability**: Every code change references spec sections
   - Commit messages include `Ref: specs/...`
   - Code comments reference spec sections
   - PR descriptions link to specifications

3. **Consistency**: Specifications prevent implementation drift
   - `make spec-check` validates alignment
   - Code reviews verify spec compliance
   - Automated validation in CI/CD

4. **Quality Assurance**: Specifications define acceptance criteria
   - Tests are derived from specs
   - Validation ensures spec alignment
   - Clear definition of "done"

5. **Onboarding**: New contributors (human or AI) can understand the project by reading specs
   - `.cursor/rules` directs AI agents to specs
   - README points to specs directory
   - Clear structure and organization

6. **Maintainability**: Specifications serve as living documentation
   - Always up-to-date (enforced by process)
   - Machine-readable (can generate docs)
   - Version-controlled (history of changes)

### Negative

1. **Upfront Investment**: Requires writing specifications before implementation
   - **Mitigation**: Specs can be lightweight and iterative
   - **Benefit**: Prevents rework and confusion

2. **Spec Maintenance**: Specifications must be kept in sync with code
   - **Mitigation**: Process requires spec updates before code changes
   - **Benefit**: Prevents drift and confusion

3. **Learning Curve**: Team must learn SDD methodology
   - **Mitigation**: Clear documentation in `specs/_meta.md` and `.cursor/rules`
   - **Benefit**: Consistent approach across team

4. **Potential Over-Specification**: Risk of over-engineering specifications
   - **Mitigation**: Start with minimal specs, iterate as needed
   - **Benefit**: Better than under-specification

### Neutral

- **Development Speed**: Initially slower (specs first), but faster long-term (less rework)
- **Tooling**: Requires spec validation tools (we use `make spec-check`)
- **Process Discipline**: Requires adherence to Prime Directive

---

## Implementation Notes

### Spec Directory Structure

```
specs/
├── _meta.md              # Master specification and vision
├── functional.md         # User stories and requirements
├── technical.md          # API contracts and data models
├── openclaw_integration.md # Network integration plan
├── database/
│   ├── schema.sql        # Database schema
│   └── erd.md           # Entity-relationship diagram
├── api/
│   └── orchestrator.yaml # OpenAPI specification
└── skills/
    └── README.md        # Skill contract definitions
```

### Prime Directive Enforcement

1. **`.cursor/rules`**: AI co-pilot rules enforce Prime Directive
2. **Code Review**: Reviewers verify spec references in PRs
3. **CI/CD**: Automated validation (future: `make spec-check` in pipeline)
4. **Documentation**: README and CONTRIBUTING.md emphasize SDD

### Traceability Mechanisms

1. **Commit Messages**: Include `Ref: specs/...` in commit body
2. **Code Comments**: Reference spec sections in docstrings
3. **PR Descriptions**: Link to relevant spec sections
4. **Test Docstrings**: Reference acceptance criteria from specs

### Spec Update Process

**Before Implementation**:
1. Update `specs/functional.md` for new user stories
2. Update `specs/technical.md` for API contracts
3. Get spec approval (if major change)
4. Implement according to spec

**After Implementation** (bug fixes only):
1. Fix bug in code
2. Update spec to reflect correct behavior
3. Ensure tests match updated spec

### Validation

- **Manual**: Code review checks spec alignment
- **Automated** (future): `make spec-check` validates:
  - Pydantic models match JSON Schema in specs
  - API routes match OpenAPI spec
  - Database schema matches `specs/database/schema.sql`

---

## Examples

### Example 1: Adding a New Skill

**Spec First** (`specs/functional.md`):
```markdown
## US-010: Schedule Engagement Posts

**As a** Chimera agent  
**I want to** schedule engagement posts for future publication  
**So that** I can maintain consistent presence without real-time monitoring

**Acceptance Criteria**:
- Agent can schedule posts with timestamp
- Posts are queued in Redis
- Posts are published at scheduled time
- Failed posts are retried with exponential backoff
```

**Then Implementation**:
- Code references `specs/functional.md US-010`
- Tests verify acceptance criteria
- PR description links to spec

### Example 2: API Contract

**Spec First** (`specs/technical.md`):
```yaml
POST /api/v1/engagement/schedule
Request:
  {
    "platform": "twitter",
    "content": "Hello world",
    "scheduled_at": "2026-02-07T10:00:00Z"
  }
Response:
  {
    "scheduled_id": "uuid",
    "status": "scheduled",
    "scheduled_at": "2026-02-07T10:00:00Z"
  }
```

**Then Implementation**:
- FastAPI route matches spec exactly
- Pydantic models match JSON Schema
- Tests verify contract compliance

---

## References

- **Master Specification**: `specs/_meta.md` defines SDD principles
- **AI Co-Pilot Rules**: `.cursor/rules` enforces Prime Directive
- **Contributing Guide**: `CONTRIBUTING.md` describes SDD workflow
- **Research**: Task 1 research validated SDD approach for AI agent development

---

## Related ADRs

- **ADR-001**: Hybrid Database Architecture (specs define database requirements)

---

**Decision Record Template**: Based on [adr.github.io](https://adr.github.io/) format.
