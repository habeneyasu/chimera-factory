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

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies
RUN uv sync --frozen

# Copy application code
COPY . .

# Install the package in editable mode
RUN uv pip install -e .

# Default command (can be overridden in docker-compose)
CMD ["python", "-m", "pytest", "tests/", "-v"]
