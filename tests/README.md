# Project Chimera: Test Suite

**Reference**: `docs/TEST_CRITERIA.md` for comprehensive test criteria

---

## Test Directory Structure

```
tests/
├── unit/              # Unit tests (fast, isolated)
├── integration/       # Integration tests (APIs, databases)
├── contracts/        # Contract tests (API/Skill validation)
└── e2e/              # End-to-end tests (full workflows)
```

## Test Types

### Unit Tests (`tests/unit/`)

- **Purpose**: Test individual functions and methods in isolation
- **Speed**: Fast (<100ms each)
- **Dependencies**: None (no external services)
- **Run**: `make test-unit` or `uv run pytest tests/unit/ -v`

**Example**:
```python
def test_example_function():
    """Test a simple function."""
    result = add(2, 3)
    assert result == 5
```

### Integration Tests (`tests/integration/`)

- **Purpose**: Test component interactions (APIs, databases, external services)
- **Speed**: Medium (may require setup/teardown)
- **Dependencies**: Docker containers, test databases, mocks
- **Run**: `make test-integration` or `uv run pytest tests/integration/ -v -m integration`

**Example**:
```python
@pytest.mark.integration
def test_api_endpoint():
    """Test API endpoint interaction."""
    response = client.post("/api/v1/trends/research", json={...})
    assert response.status_code == 200
```

### Contract Tests (`tests/contracts/`)

- **Purpose**: Validate that implementations match specifications
- **Coverage**: API contracts, Skill contracts, Database schema
- **Run**: `make test-contracts` or `uv run pytest tests/contracts/ -v -m contracts`

**Example**:
```python
def test_skill_input_contract():
    """Test skill input matches contract JSON Schema."""
    input_data = {"topic": "AI", "sources": ["twitter"]}
    # Validate against skills/skill_trend_research/contract.json
```

### End-to-End Tests (`tests/e2e/`)

- **Purpose**: Test complete workflows from start to finish
- **Speed**: Slow (full system setup required)
- **Dependencies**: All services running
- **Run**: `make test-e2e` or `uv run pytest tests/e2e/ -v -m e2e`

**Example**:
```python
@pytest.mark.e2e
def test_trend_to_content_workflow():
    """Test complete trend-to-content workflow."""
    # 1. Research trends
    # 2. Create content plan
    # 3. Generate content
    # 4. Approval workflow
```

## Running Tests

### Run All Tests
```bash
make test-all
# or
uv run pytest tests/ -v --cov=src/chimera_factory
```

### Run Specific Test Type
```bash
make test-unit          # Unit tests only
make test-integration   # Integration tests only
make test-contracts     # Contract tests only
make test-e2e           # E2E tests only
```

### Run Tests with Markers
```bash
# Run only unit tests
uv run pytest -m unit

# Run only integration tests
uv run pytest -m integration

# Run only contract tests
uv run pytest -m contracts

# Run only E2E tests
uv run pytest -m e2e

# Skip slow tests
uv run pytest -m "not slow"
```

### Run Specific Test File
```bash
uv run pytest tests/unit/test_example.py -v
```

### Run with Coverage
```bash
uv run pytest tests/ -v --cov=src/chimera_factory --cov-report=html
# Open htmlcov/index.html in browser
```

## Test Writing Guidelines

### 1. Reference Specifications

All tests must reference specifications:

```python
def test_trend_research():
    """
    Test trend research functionality.
    
    Reference: specs/functional.md US-001
    Reference: specs/technical.md (Trend Research API)
    """
    # Test implementation
```

### 2. Use Descriptive Names

```python
# Good
def test_trend_research_returns_structured_data():
    """Test that trend research returns structured data."""
    pass

# Bad
def test_trend():
    """Test trend."""
    pass
```

### 3. Follow Test Criteria

All tests should align with test criteria in `docs/TEST_CRITERIA.md`:

- **Functional Tests**: Validate user story acceptance criteria
- **API Tests**: Validate JSON Schema contracts
- **Skill Tests**: Validate input/output contracts
- **Database Tests**: Validate schema and data integrity

### 4. Use Fixtures for Test Data

```python
@pytest.fixture
def sample_trend_data():
    """Fixture providing sample trend data."""
    return {
        "topic": "AI influencers",
        "sources": ["twitter"],
        "timeframe": "24h"
    }

def test_trend_research(sample_trend_data):
    """Test trend research with fixture data."""
    result = research_trends(sample_trend_data)
    assert result is not None
```

### 5. Mark Tests Appropriately

```python
@pytest.mark.unit
def test_fast_function():
    """Fast unit test."""
    pass

@pytest.mark.integration
def test_api_integration():
    """Integration test requiring external services."""
    pass

@pytest.mark.slow
def test_performance():
    """Slow performance test."""
    pass
```

## Test Coverage Targets

- **Code Coverage**: 80%+ for all modules
- **API Coverage**: 100% of all endpoints
- **Skill Coverage**: 100% of all skills
- **User Story Coverage**: 100% of all user stories

## Continuous Integration

All tests run in CI/CD pipeline:
- **Unit tests**: On every commit
- **Integration tests**: On every PR
- **Contract tests**: On every PR
- **E2E tests**: Before merge
- **Performance tests**: Weekly

## Test Maintenance

- Update tests when specs change
- Remove obsolete tests
- Add tests for new features
- Keep test documentation up-to-date

---

**For comprehensive test criteria, see**: `docs/TEST_CRITERIA.md`
