# Dockerfile: Project Chimera
# Multi-stage build for optimized containerization
# Prepared By: habeneyasu
# Repository: https://github.com/habeneyasu/chimera-factory

# ============================================================================
# Stage 1: Builder - Install dependencies and build package
# ============================================================================
FROM python:3.12-slim AS builder

# Install system dependencies for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv

# Set working directory
WORKDIR /app

# Copy dependency files (for better layer caching)
COPY pyproject.toml uv.lock ./

# Verify uv.lock exists (explicit dependency locking)
RUN if [ ! -f "uv.lock" ]; then \
        echo "ERROR: uv.lock not found. Run 'uv lock' to generate lock file."; \
        exit 1; \
    fi

# Install dependencies with frozen lock file (explicit dependency locking)
RUN uv sync --frozen --no-dev

# Copy source code for package installation
COPY src/ ./src/

# Install package in development mode (includes source)
RUN uv pip install -e .

# ============================================================================
# Stage 2: Runtime - Production API image
# ============================================================================
FROM python:3.12-slim AS runtime

# Install only runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install uv (needed for running commands)
RUN pip install --no-cache-dir uv

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY specs/ ./specs/
COPY skills/ ./skills/

# Create logs directory
RUN mkdir -p logs

# Set Python path
ENV PYTHONPATH=/app
ENV PATH="/app/.venv/bin:$PATH"

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${API_PORT:-8000}/api/v1/health || exit 1

# Default command (can be overridden in docker-compose)
CMD ["python", "scripts/run_api.py"]

# ============================================================================
# Stage 3: Test - Test-focused image with dev dependencies
# ============================================================================
FROM builder AS test

# Install test dependencies
RUN uv sync --frozen --dev

# Copy test files
COPY tests/ ./tests/
COPY .pytest.ini* pytest.ini* pyproject.toml ./

# Copy additional files needed for tests
COPY .env.example ./
COPY Makefile ./

# Set Python path
ENV PYTHONPATH=/app

# Default command for test container
CMD ["uv", "run", "pytest", "tests/", "-v", "--cov=src/chimera_factory", "--cov-report=term-missing"]
