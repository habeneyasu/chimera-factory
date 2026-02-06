# Dockerfile: Project Chimera
# Prepared By: habeneyasu
# Repository: https://github.com/habeneyasu/chimera-factory

FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv

# Set working directory
WORKDIR /app

# Copy dependency files first (for better caching)
COPY pyproject.toml uv.lock* ./

# Copy source directory structure (needed for package installation)
COPY src/ ./src/

# Install dependencies and package
RUN uv sync --frozen

# Copy remaining application code
COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose API port (default 8000, configurable via .env)
EXPOSE 8000

# Default command (can be overridden in docker-compose)
# Default to running API server, but can be overridden for tests
CMD ["uv", "run", "python", "scripts/run_api.py"]
