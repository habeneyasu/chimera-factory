# Docker Containerization Guide

**Project Chimera** is fully containerized using Docker and Docker Compose for consistent development and deployment.

## Multi-Stage Build Architecture

The Dockerfile uses a **multi-stage build** for optimized containerization:

1. **Builder Stage**: Installs dependencies and builds the package
2. **Runtime Stage**: Production API image (minimal, optimized)
3. **Test Stage**: Test-focused image with dev dependencies

### Benefits

- **Smaller Images**: Runtime image only contains production dependencies
- **Better Caching**: Dependency layers cached separately from application code
- **Explicit Dependency Locking**: `uv.lock` is verified and required
- **Test-Focused Image**: Dedicated test image with all dev dependencies

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- `.env` file configured (copy from `.env.example`)

### Start All Services

```bash
# Start all services (API, PostgreSQL, Weaviate, Redis)
make docker-up

# Or manually
docker compose up -d
```

### Access Services

- **API Server**: http://localhost:8000/api/v1/docs
- **PostgreSQL**: localhost:5433 (default, configurable via `POSTGRES_HOST_PORT`)
- **Weaviate**: http://localhost:8080 (default, configurable via `WEAVIATE_PORT`)
- **Redis**: localhost:6380 (default, configurable via `REDIS_HOST_PORT`)

**Note**: Default ports are 5433 (PostgreSQL), 8080 (Weaviate), and 6380 (Redis) to avoid conflicts with local installations. You can change these in `.env`.

### Stop Services

```bash
make docker-down

# Or manually
docker compose down
```

## Building Images

### Build All Images

```bash
# Build all images (runtime and test)
make docker-build

# Or manually
docker compose build
```

### Build Specific Stages

```bash
# Build runtime image only
make docker-build-runtime

# Build test image only
make docker-build-test

# Or manually
docker build --target runtime -t chimera-factory:runtime -f Dockerfile .
docker build --target test -t chimera-factory:test -f Dockerfile .
```

### Verify Dependency Lock File

```bash
# Verify uv.lock exists and is up to date
make docker-verify-lock

# Or manually
uv lock --check
```

**Important**: The Dockerfile requires `uv.lock` for explicit dependency locking. Always commit `uv.lock` after running `uv lock`.

## Services

### API Server

The main FastAPI application server.

```bash
# Start only API service
make docker-api

# View API logs
docker compose logs -f api

# Access API container shell
make docker-shell
```

### PostgreSQL Database

PostgreSQL database for transactional data storage.

```bash
# Start only database services
make docker-db

# Connect to database
docker compose exec postgres psql -U postgres -d chimera_dev

# View database logs
docker compose logs -f postgres
```

### Weaviate Vector Database

Weaviate for semantic memory and RAG (Retrieval-Augmented Generation).

```bash
# Access Weaviate console
open http://localhost:8080

# View Weaviate logs
docker compose logs -f weaviate
```

### Redis Cache

Redis for episodic cache and task queuing.

```bash
# Connect to Redis CLI
docker compose exec redis redis-cli

# View Redis logs
docker compose logs -f redis
```

## Running Tests

### Run Tests in Docker

```bash
# Run tests using test-focused image
make docker-test

# Run full test suite with coverage
make docker-test-full

# Or manually
docker compose --profile test run --rm test
```

The test service uses a dedicated **test-focused image** that includes:
- All dev dependencies (pytest, pytest-cov, mypy, ruff)
- Test files and configuration
- Coverage reporting tools

### Test Image Benefits

- **Isolated Environment**: Tests run in a clean, reproducible environment
- **CI/CD Ready**: Same image used in GitHub Actions CI pipeline
- **Fast Iteration**: Test image cached separately from runtime image
- **Full Coverage**: All test dependencies included

## Configuration

All configuration is loaded from `.env` file. The following environment variables are used:

### API Configuration
- `API_HOST`: Server host (default: `0.0.0.0`)
- `API_PORT`: Server port (default: `8000`)
- `API_RELOAD`: Enable auto-reload (default: `false` in Docker)
- `API_WORKERS`: Number of workers (default: `4`)
- `LOG_LEVEL`: Logging level (default: `info`)
- `CORS_ORIGINS`: Allowed CORS origins (default: `*`)

### Database Configuration
- `POSTGRES_DB`: Database name (default: `chimera_dev`)
- `POSTGRES_USER`: Database user (default: `postgres`)
- `POSTGRES_PASSWORD`: Database password (required)
- `POSTGRES_PORT`: Database port inside container (default: `5432`)
- `POSTGRES_HOST_PORT`: Host port mapping (default: `5433` to avoid conflicts)

### Weaviate Configuration
- `WEAVIATE_URL`: Weaviate server URL (default: `http://weaviate:8080` in Docker)
- `WEAVIATE_API_KEY`: Weaviate API key (optional, for authentication)
- `WEAVIATE_PORT`: Host port mapping (default: `8080`)

### Redis Configuration
- `REDIS_HOST`: Redis host (default: `redis` in Docker)
- `REDIS_PORT`: Redis port inside container (default: `6379`)
- `REDIS_HOST_PORT`: Host port mapping (default: `6380` to avoid conflicts)
- `REDIS_DB`: Redis database number (default: `0`)

## Development

### Local Development Override

For local development, create `docker-compose.override.yml`:

```bash
cp docker-compose.override.yml.example docker-compose.override.yml
# Edit with your local settings
```

This allows you to:
- Enable auto-reload for faster development
- Mount source code for live editing
- Override port mappings
- Adjust logging levels

### Running Tests

```bash
# Run tests in Docker
make docker-test

# Or manually
docker compose --profile test run --rm test
```

### Building Images

```bash
# Build all images
make docker-build

# Or manually
docker compose build
```

## Makefile Commands

All Docker operations are available via Makefile:

```bash
make docker-up          # Start all services
make docker-down        # Stop all services
make docker-build       # Build Docker images
make docker-logs        # View logs from all services
make docker-ps          # List running containers
make docker-api         # Start only API service
make docker-db          # Start database services
make docker-test        # Run tests in Docker container
make docker-shell       # Open shell in API container
```

## Volumes

Docker Compose creates persistent volumes for:

- `postgres_data`: PostgreSQL data directory
- `weaviate_data`: Weaviate data directory
- `redis_data`: Redis data directory
- `logs`: Application logs

To remove volumes (⚠️ **deletes all data**):

```bash
docker compose down -v
```

## Health Checks

All services include health checks:

- **PostgreSQL**: Checks if database is ready
- **Weaviate**: Checks if Weaviate is ready
- **Redis**: Checks if Redis is responding
- **API**: Checks if API health endpoint responds

Services wait for dependencies to be healthy before starting.

## Troubleshooting

### Port Already in Use

If ports are already in use, update `.env`:

```bash
API_PORT=8080
POSTGRES_HOST_PORT=5434  # Change host port mapping
REDIS_HOST_PORT=6381     # Change host port mapping
```

**Note**: The default ports (5433 for PostgreSQL, 8080 for Weaviate, 6380 for Redis) are chosen to avoid conflicts with common local installations. Inside containers, services still use standard ports (5432, 8080, 6379).

### Database Connection Issues

Check database is running:

```bash
docker compose ps
docker compose logs postgres
```

### API Not Starting

Check API logs:

```bash
docker compose logs api
```

### Reset Everything

```bash
# Stop and remove everything (including volumes)
docker compose down -v

# Rebuild and start
make docker-build
make docker-up
```

## Production Deployment

For production:

1. Set `API_RELOAD=false` in `.env`
2. Set appropriate `API_WORKERS` (e.g., `4`)
3. Configure proper `CORS_ORIGINS` (not `*`)
4. Use strong passwords for database
5. Configure proper logging levels
6. Set up volume backups for PostgreSQL, Weaviate, and Redis

---

**Reference**: See `docker-compose.yml` and `Dockerfile` for detailed configuration.
