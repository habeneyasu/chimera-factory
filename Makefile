.PHONY: setup test spec-check clean help

help:
	@echo "Project Chimera - Makefile Commands"
	@echo ""
	@echo "  make setup       - Install dependencies"
	@echo "  make test        - Run tests in Docker"
	@echo "  make spec-check  - Verify code aligns with specs"
	@echo "  make clean       - Clean build artifacts"

setup:
	@echo "Installing dependencies..."
	uv sync
	@echo "✓ Dependencies installed"

test:
	@echo "Running tests in Docker..."
	@if [ -f "docker-compose.yml" ]; then \
		docker compose run --rm test; \
	else \
		echo "ERROR: docker-compose.yml not found"; \
		exit 1; \
	fi

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

clean:
	@echo "Cleaning build artifacts..."
	rm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@echo "✓ Clean complete"
