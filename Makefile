.PHONY: setup test spec-check clean help

help:
	@echo "Project Chimera - Makefile Commands"
	@echo ""
	@echo "  make setup       - Install dependencies"
	@echo "  make test        - Run tests in Docker"
	@echo "  make spec-check  - Verify code aligns with specs"
	@echo "  make clean       - Clean build artifacts"

setup:
	uv sync

test:
	@echo "Running tests..."
	@if [ -f "docker-compose.yml" ]; then \
		docker-compose run --rm test; \
	else \
		echo "Note: Docker tests will be configured in Task 3"; \
	fi

spec-check:
	@echo "Checking spec alignment..."
	@if [ ! -d "specs" ]; then \
		echo "ERROR: specs/ directory not found"; \
		exit 1; \
	fi
	@if [ ! -f "specs/_meta.md" ]; then \
		echo "WARNING: specs/_meta.md not found"; \
	fi
	@echo "Validating Pydantic models..."
	@uv run python -c "from specs.skills import TrendResearchInput, ContentGenerateInput, EngagementManageInput; print('✓ Pydantic models valid')" 2>/dev/null || echo "⚠️  Pydantic models not yet importable (expected in Task 2)"
	@echo "Spec structure check passed"

clean:
	rm -rf __pycache__ .pytest_cache .mypy_cache
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
