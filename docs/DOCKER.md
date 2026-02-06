# Docker Containerization Guide

**Project Chimera** is fully containerized using Docker and Docker Compose for consistent development and deployment.

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- `.env` file configured (copy from `.env.example`)

### Start All Services

```bash
# Start all services (API, PostgreSQL, Redis)
make docker-up

# Or manually
docker compose up -d
```

### Access Services

- **API Server**: http://localhost:8000/api/v1/docs
- **PostgreSQL**: localhost:5433 (default, configurable via `POSTGRES_HOST_PORT`)
- **Redis**: localhost:6380 (default, configurable via `REDIS_HOST_PORT`)

**Note**: Default ports are 5433 and 6380 to avoid conflicts with local PostgreSQL/Redis installations. You can change these in `.env`.

### Stop Services

```bash
make docker-down

# Or manually
docker compose down
```

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

PostgreSQL database for persistent data storage.

```bash
# Start only database services
make docker-db

# Connect to database
docker compose exec postgres psql -U postgres -d chimera_dev

# View database logs
docker compose logs -f postgres
```

### Redis Cache

Redis for caching and rate limiting.

```bash
# Connect to Redis CLI
docker compose exec redis redis-cli

# View Redis logs
docker compose logs -f redis
```

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
- `redis_data`: Redis data directory
- `logs`: Application logs

To remove volumes (⚠️ **deletes all data**):

```bash
docker compose down -v
```

## Health Checks

All services include health checks:

- **PostgreSQL**: Checks if database is ready
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

**Note**: The default ports (5433 for PostgreSQL, 6380 for Redis) are chosen to avoid conflicts with common local installations. Inside containers, services still use standard ports (5432, 6379).

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
6. Set up volume backups for PostgreSQL and Redis

---

**Reference**: See `docker-compose.yml` and `Dockerfile` for detailed configuration.
