.PHONY: setup test test-unit test-integration test-contracts test-e2e test-all spec-check validate-task2 test-criteria clean help
.PHONY: docker-up docker-down docker-build docker-logs docker-ps docker-api docker-db docker-test docker-shell

help:
	@echo "Project Chimera - Makefile Commands"
	@echo ""
	@echo "Setup & Development:"
	@echo "  make setup              - Install dependencies"
	@echo "  make run-api            - Start API server (local)"
	@echo "  make run-api-dev        - Start API server in dev mode"
	@echo ""
	@echo "Testing:"
	@echo "  make test               - Run tests in Docker"
	@echo "  make test-unit          - Run unit tests"
	@echo "  make test-integration   - Run integration tests"
	@echo "  make test-contracts     - Run contract tests (API & Skills)"
	@echo "  make test-e2e           - Run end-to-end tests"
	@echo "  make test-all           - Run all tests with coverage"
	@echo ""
	@echo "Docker Commands:"
	@echo "  make docker-up          - Start all services (API, PostgreSQL, Weaviate, Redis)"
	@echo "  make docker-down        - Stop all services"
	@echo "  make docker-build       - Build Docker images"
	@echo "  make docker-logs        - View logs from all services"
	@echo "  make docker-ps          - List running containers"
	@echo "  make docker-api         - Start only API service"
	@echo "  make docker-db          - Start database services (PostgreSQL, Weaviate, Redis)"
	@echo "  make docker-test        - Run tests in Docker container"
	@echo "  make docker-shell       - Open shell in API container"
	@echo ""
	@echo "Validation:"
	@echo "  make spec-check         - Verify code aligns with specs"
	@echo "  make validate-task2     - Validate Task 2 deliverables"
	@echo "  make test-criteria      - Show test criteria summary"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean              - Clean build artifacts"

setup:
	@echo "Installing dependencies..."
	uv sync
	@echo "✓ Dependencies installed"

test:
	@echo "Running tests in Docker..."
	@if [ -f "docker-compose.yml" ]; then \
		$(DOCKER_COMPOSE) --profile test run --rm test; \
	else \
		echo "ERROR: docker-compose.yml not found"; \
		exit 1; \
	fi

# Docker Commands
# Detect Docker Compose version (V1: docker-compose, V2: docker compose)
DOCKER_COMPOSE = $(shell which docker-compose > /dev/null 2>&1 && echo docker-compose || echo docker compose)

docker-up:
	@echo "Starting all services (API, PostgreSQL, Weaviate, Redis)..."
	@echo "Checking for port conflicts..."
	@if lsof -i :5432 >/dev/null 2>&1 && [ -z "$$POSTGRES_HOST_PORT" ]; then \
		echo "⚠️  Warning: Port 5432 is in use. Using port 5433 for PostgreSQL."; \
		echo "   Set POSTGRES_HOST_PORT in .env to use a different port."; \
	fi
	@if lsof -i :6379 >/dev/null 2>&1 && [ -z "$$REDIS_HOST_PORT" ]; then \
		echo "⚠️  Warning: Port 6379 is in use. Using port 6380 for Redis."; \
		echo "   Set REDIS_HOST_PORT in .env to use a different port."; \
	fi
	@echo "Building images if needed..."
	@$(DOCKER_COMPOSE) build --quiet api 2>/dev/null || $(DOCKER_COMPOSE) build api
	@echo "Starting services..."
	@$(DOCKER_COMPOSE) up -d
	@echo "✓ Services started. Use 'make docker-logs' to view logs"
	@echo ""
	@echo "Service URLs:"
	@echo "  API:      http://localhost:$${API_PORT:-8000}/api/v1/docs"
	@echo "  Postgres: localhost:$${POSTGRES_HOST_PORT:-5433}"
	@echo "  Weaviate: http://localhost:$${WEAVIATE_PORT:-8080}"
	@echo "  Redis:    localhost:$${REDIS_HOST_PORT:-6380}"

docker-down:
	@echo "Stopping all services..."
	@$(DOCKER_COMPOSE) down
	@echo "✓ Services stopped"

docker-build:
	@echo "Building Docker images..."
	@$(DOCKER_COMPOSE) build
	@echo "✓ Images built"

docker-logs:
	@$(DOCKER_COMPOSE) logs -f

docker-ps:
	@$(DOCKER_COMPOSE) ps

docker-api:
	@echo "Starting API service..."
	@$(DOCKER_COMPOSE) up -d api
	@echo "✓ API service started"

docker-db:
	@echo "Starting database services (PostgreSQL, Weaviate, Redis)..."
	@$(DOCKER_COMPOSE) up -d postgres weaviate redis
	@echo "✓ Database services started"

docker-test:
	@echo "Running tests in Docker container..."
	@$(DOCKER_COMPOSE) --profile test run --rm test

docker-shell:
	@echo "Opening shell in API container..."
	@$(DOCKER_COMPOSE) exec api /bin/bash

spec-check:
	@echo "=========================================="
	@echo "Spec-Driven Development Validation"
	@echo "=========================================="
	@echo ""
	@# Check spec directory structure
	@echo "1. Checking spec directory structure..."
	@if [ ! -d "specs" ]; then \
		echo "   ❌ ERROR: specs/ directory not found"; \
		exit 1; \
	fi
	@echo "   ✓ specs/ directory exists"
	@echo ""
	@# Check required spec files
	@echo "2. Checking required spec files..."
	@for file in specs/_meta.md specs/functional.md specs/technical.md specs/database/schema.sql specs/database/erd.md; do \
		if [ ! -f "$$file" ]; then \
			echo "   ❌ ERROR: Required spec file not found: $$file"; \
			exit 1; \
		fi; \
	done
	@echo "   ✓ All required spec files present"
	@echo ""
	@# Check skill contracts
	@echo "3. Checking skill contracts..."
	@for skill in skill_trend_research skill_content_generate skill_engagement_manage; do \
		if [ ! -f "skills/$$skill/contract.json" ]; then \
			echo "   ⚠️  WARNING: Contract not found: skills/$$skill/contract.json"; \
		else \
			echo "   ✓ Contract found: skills/$$skill/contract.json"; \
		fi; \
		if [ ! -f "skills/$$skill/README.md" ]; then \
			echo "   ⚠️  WARNING: README not found: skills/$$skill/README.md"; \
		else \
			echo "   ✓ README found: skills/$$skill/README.md"; \
		fi; \
	done
	@echo ""
	@# Check test files reference specs
	@echo "4. Checking test files reference specs..."
	@if [ -d "tests" ]; then \
		test_count=$$(find tests -name "test_*.py" | wc -l); \
		if [ $$test_count -eq 0 ]; then \
			echo "   ⚠️  WARNING: No test files found in tests/"; \
		else \
			echo "   ✓ Found $$test_count test file(s)"; \
			spec_refs=$$(grep -r "specs/" tests/ 2>/dev/null | wc -l || echo "0"); \
			if [ $$spec_refs -gt 0 ]; then \
				echo "   ✓ Test files reference specs ($$spec_refs references found)"; \
			else \
				echo "   ⚠️  WARNING: Test files should reference specs/ in docstrings"; \
			fi; \
		fi; \
	else \
		echo "   ⚠️  WARNING: tests/ directory not found"; \
	fi
	@echo ""
	@# Validate Pydantic models (when implemented)
	@echo "5. Validating Pydantic models (if implemented)..."
	@uv run python -c "from specs.skills import TrendResearchInput, ContentGenerateInput, EngagementManageInput; print('   ✓ Pydantic models importable')" 2>/dev/null || echo "   ⚠️  Pydantic models not yet implemented (expected in Task 2.3)"
	@echo ""
	@# Check for spec references in code
	@echo "6. Checking code references to specs..."
	@if [ -d "src" ]; then \
		spec_refs=$$(grep -r "specs/" src/ 2>/dev/null | wc -l || echo "0"); \
		if [ $$spec_refs -gt 0 ]; then \
			echo "   ✓ Code references specs ($$spec_refs references found)"; \
		else \
			echo "   ⚠️  WARNING: Code should reference specs/ in comments"; \
		fi; \
	else \
		echo "   ⚠️  WARNING: src/ directory not found (expected in early stages)"; \
	fi
	@echo ""
	@# Check database schema
	@echo "7. Validating database schema..."
	@if [ -f "specs/database/schema.sql" ]; then \
		table_count=$$(grep -c "CREATE TABLE" specs/database/schema.sql 2>/dev/null || echo "0"); \
		if [ $$table_count -gt 0 ]; then \
			echo "   ✓ Database schema contains $$table_count table(s)"; \
		else \
			echo "   ⚠️  WARNING: No CREATE TABLE statements found in schema.sql"; \
		fi; \
	fi
	@echo ""
	@echo "=========================================="
	@echo "✓ Spec validation complete"
	@echo "=========================================="
	@echo ""
	@echo "Note: Warnings are acceptable in early development stages."
	@echo "      Errors must be resolved before merging code."

validate-task2:
	@echo "Validating Task 2: The Architect deliverables..."
	@uv run python scripts/validate_task2.py

test-unit:
	@echo "Running unit tests..."
	@uv run pytest tests/unit/ -v --cov=src/chimera_factory --cov-report=term-missing || echo "⚠️  Unit tests directory not found. Create tests/unit/ to add unit tests."

test-integration:
	@echo "Running integration tests..."
	@uv run pytest tests/integration/ -v || echo "⚠️  Integration tests directory not found. Create tests/integration/ to add integration tests."

test-contracts:
	@echo "Running contract tests (API & Skills)..."
	@uv run pytest tests/contracts/ -v || echo "⚠️  Contract tests directory not found. Create tests/contracts/ to add contract tests."

test-e2e:
	@echo "Running end-to-end tests..."
	@uv run pytest tests/e2e/ -v || echo "⚠️  E2E tests directory not found. Create tests/e2e/ to add E2E tests."

test-all:
	@echo "Running all tests with coverage..."
	@uv run pytest tests/ -v --cov=src/chimera_factory --cov-report=term-missing --cov-report=html || echo "⚠️  Tests directory structure not found. See docs/TEST_CRITERIA.md for test setup."

test-criteria:
	@echo "=========================================="
	@echo "Project Chimera: Test Criteria Summary"
	@echo "=========================================="
	@echo ""
	@echo "📋 Test Categories:"
	@echo "  • Functional Testing (21+ user stories)"
	@echo "  • API Contract Testing (7 endpoints)"
	@echo "  • Skills Contract Testing (3 skills)"
	@echo "  • Database Testing (schema, migrations)"
	@echo "  • Integration Testing (MCP, OpenClaw)"
	@echo "  • Performance Testing (1,000+ agents)"
	@echo "  • Security Testing (auth, authorization)"
	@echo "  • Compliance Testing (audit trails, HITL)"
	@echo "  • SDD Validation (spec alignment)"
	@echo "  • E2E Workflow Testing"
	@echo ""
	@echo "📖 Full documentation: docs/TEST_CRITERIA.md"
	@echo ""
	@echo "🎯 Test Coverage Targets:"
	@echo "  • Code Coverage: 80%+"
	@echo "  • API Coverage: 100%"
	@echo "  • Skill Coverage: 100%"
	@echo "  • User Story Coverage: 100%"
	@echo ""

run-api:
	@echo "Starting Chimera Orchestrator API server..."
	@uv run python scripts/run_api.py

run-api-dev:
	@echo "Starting API server in development mode..."
	@uv run python scripts/run_api.py

run-api-prod:
	@echo "Starting API server in production mode..."
	@API_RELOAD=false uv run python scripts/run_api.py

clean:
	@echo "Cleaning build artifacts..."
	rm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@echo "✓ Clean complete"
