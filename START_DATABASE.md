# Starting Database for Tests

The tests require PostgreSQL and Redis to be running. Here's how to start them:

## Option 1: Using Makefile (Recommended)

```bash
# Start only database services (PostgreSQL and Redis)
make docker-db

# Or start all services
make docker-up
```

## Option 2: Using Docker Compose Directly

```bash
# Detect Docker Compose version
DOCKER_COMPOSE=$(which docker-compose > /dev/null 2>&1 && echo docker-compose || echo docker compose)

# Start only database services
$DOCKER_COMPOSE up -d postgres redis

# Or start all services
$DOCKER_COMPOSE up -d
```

## Verify Services Are Running

```bash
# Check running containers
docker ps | grep -E "postgres|redis"

# Check if ports are accessible
lsof -i :5433  # PostgreSQL
lsof -i :6380  # Redis
```

## Troubleshooting

If you get permission errors:
```bash
# Use sudo
sudo make docker-db

# Or add your user to docker group (requires logout/login)
sudo usermod -aG docker $USER
```

## After Starting Services

Once the services are running, you can run the tests:

```bash
make test
# or
uv run pytest tests/integration/ -v
```
