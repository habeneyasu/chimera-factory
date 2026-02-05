# Dockerfile: Project Chimera
# Prepared By: habeneyasu
# Repository: https://github.com/habeneyasu/chimera-factory

FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
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

# Default command (can be overridden in docker-compose)
CMD ["uv", "run", "pytest", "tests/", "-v"]
