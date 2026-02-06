"""
Database connection management for Project Chimera.

Reference: specs/database/schema.sql
"""

import os
from psycopg2.pool import ThreadedConnectionPool
from typing import Optional
from contextlib import contextmanager
from dotenv import load_dotenv, find_dotenv

# Load environment variables from .env file
# Use find_dotenv to locate the .env file in the project root
# override=False ensures Docker Compose environment variables take precedence
# Detect if we're inside Docker by checking for Docker-specific environment variables
# or if POSTGRES_HOST is already set to "postgres" (Docker service name)
_is_inside_docker = (
    os.getenv("POSTGRES_HOST") == "postgres" or
    os.path.exists("/.dockerenv") or
    os.getenv("DOCKER_CONTAINER") == "true"
)

# Only load .env if we're NOT inside Docker
# This prevents .env from potentially interfering with Docker Compose environment variables
if not _is_inside_docker:
    load_dotenv(find_dotenv(), override=False)

# Connection pool (initialized on first use)
_connection_pool: Optional[ThreadedConnectionPool] = None
_connection_string: Optional[str] = None  # Track connection string to detect changes


def get_connection_string() -> str:
    """
    Get PostgreSQL connection string from environment variables.
    
    Reads from POSTGRES_CONNECTION_STRING or constructs from individual
    POSTGRES_* environment variables.
    
    Environment variables:
    - POSTGRES_CONNECTION_STRING: Full connection string (preferred)
    - POSTGRES_HOST: Database host (default: localhost)
    - POSTGRES_HOST_PORT: Host port for PostgreSQL (used when connecting from host, e.g., 5433)
    - POSTGRES_PORT: Database port (default: 5432, used when inside Docker container)
    - POSTGRES_DB: Database name (default: chimera_dev)
    - POSTGRES_USER: Database user (default: postgres)
    - POSTGRES_PASSWORD: Database password (required)
    
    Note: POSTGRES_HOST_PORT takes precedence over POSTGRES_PORT when connecting
    from outside Docker (e.g., local tests). Inside Docker, use POSTGRES_PORT.
    
    Returns:
        Connection string in format: postgresql://user:password@host:port/database
        
    Raises:
        ValueError: If required environment variables are missing
    """
    # Try full connection string first
    conn_str = os.getenv("POSTGRES_CONNECTION_STRING")
    if conn_str:
        # If POSTGRES_CONNECTION_STRING is set, fix port for localhost if needed
        import re
        
        # Check if it's a localhost connection with port 5432
        if ("localhost" in conn_str or "127.0.0.1" in conn_str) and ":5432" in conn_str:
            # Use regex to replace port 5432 with 5433 for localhost connections
            # Also replace localhost with 127.0.0.1 to force IPv4
            # Match patterns like: @localhost:5432/ or @localhost:5432? or @127.0.0.1:5432/
            original_conn_str = conn_str
            # First fix port
            conn_str = re.sub(
                r'@(localhost|127\.0\.0\.1):5432(/|\?|$)',
                r'@\1:5433\2',
                conn_str
            )
            # Then replace localhost with 127.0.0.1 to force IPv4
            conn_str = re.sub(
                r'@localhost:',
                r'@127.0.0.1:',
                conn_str
            )
            
            if conn_str != original_conn_str:
                import logging
                logger = logging.getLogger(__name__)
                logger.info(
                    f"Updated POSTGRES_CONNECTION_STRING: port 5432->5433, localhost->127.0.0.1 for IPv4 connection"
                )
        
        return conn_str
    
    # Construct from individual variables
    # IMPORTANT: Docker Compose sets POSTGRES_HOST=postgres for test service
    # We need to ensure .env doesn't override this
    host = os.getenv("POSTGRES_HOST", "localhost")
    
    # Detect if we're inside Docker
    is_inside_docker = (
        os.path.exists("/.dockerenv") or
        os.getenv("DOCKER_CONTAINER") == "true" or
        host == "postgres"
    )
    
    # If inside Docker but host is not "postgres", something is wrong
    if is_inside_docker and host != "postgres" and host != "localhost":
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(
            f"Inside Docker but POSTGRES_HOST={host} (expected 'postgres'). "
            f"Using 'postgres' as fallback."
        )
        host = "postgres"
    
    # Force IPv4 for localhost to avoid IPv6 connection issues
    # Use 127.0.0.1 instead of localhost to ensure IPv4 connection
    # BUT: Don't convert if host is "postgres" (Docker service name)
    if host == "localhost":
        host = "127.0.0.1"
    
    # Determine port based on connection context:
    # - host == "postgres": Inside Docker, ALWAYS use container port (5432), ignore POSTGRES_HOST_PORT
    # - POSTGRES_HOST_PORT: Explicitly set host port (for local Docker connections from host)
    # - host == "127.0.0.1": Local connection, prefer POSTGRES_HOST_PORT, then default to 5433
    # - Otherwise: Use POSTGRES_PORT or default to 5432
    host_port = os.getenv("POSTGRES_HOST_PORT")
    container_port = os.getenv("POSTGRES_PORT")
    
    # Debug logging
    import logging
    import sys
    logger = logging.getLogger(__name__)
    logger.debug(f"Connection config - host: {host}, host_port: {host_port}, container_port: {container_port}")
    # Also print to stderr for immediate visibility in tests
    if "pytest" in sys.modules:
        print(f"DEBUG Connection config - host: {host}, host_port: {host_port}, container_port: {container_port}", file=sys.stderr)
        print(f"DEBUG POSTGRES_HOST env var: {os.getenv('POSTGRES_HOST', 'NOT SET')}", file=sys.stderr)
    
    # IMPORTANT: Inside Docker, POSTGRES_HOST should be "postgres" (service name)
    # and we should use container port (5432), NOT host port (5433)
    # POSTGRES_HOST_PORT should only be used when connecting from host machine
    if host == "postgres":
        # Inside Docker container, use container port (5432)
        # Ignore POSTGRES_HOST_PORT as it's for host connections only
        port = container_port or "5432"
        logger.info(f"Inside Docker: Using 'postgres' host with container port: {port}")
    elif host_port and host != "postgres":
        # Explicitly set host port takes priority for non-Docker connections
        port = host_port
        logger.debug(f"Using POSTGRES_HOST_PORT: {port}")
    elif host == "127.0.0.1":
        # Local connection to Docker from host - use host port if set, otherwise default to 5433
        # (Don't use POSTGRES_PORT here as it's for container port, not host port)
        port = host_port or "5433"
        logger.debug(f"Using host port for 127.0.0.1: {port}")
    else:
        # Other hosts - use container port or default
        port = container_port or "5432"
        logger.debug(f"Using container port for other host: {port}")
    
    database = os.getenv("POSTGRES_DB", "chimera_dev")
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD")
    
    if not password:
        raise ValueError(
            "POSTGRES_PASSWORD or POSTGRES_CONNECTION_STRING must be set in environment"
        )
    
    # URL-encode password (handle special characters like @)
    from urllib.parse import quote_plus
    encoded_password = quote_plus(password)
    
    conn_str = f"postgresql://{user}:{encoded_password}@{host}:{port}/{database}"
    
    # Debug: Log connection string (without password) for troubleshooting
    import logging
    import sys
    logger = logging.getLogger(__name__)
    debug_msg = f"Database connection: postgresql://{user}:***@{host}:{port}/{database}"
    logger.info(debug_msg)  # Changed to info for better visibility
    # Also print to stderr for immediate visibility in tests
    if "pytest" in sys.modules:
        print(f"DEBUG: {debug_msg}", file=sys.stderr)
    
    return conn_str


def init_connection_pool(minconn: int = 1, maxconn: int = 10) -> ThreadedConnectionPool:
    """
    Initialize database connection pool.
    
    Args:
        minconn: Minimum number of connections
        maxconn: Maximum number of connections
        
    Returns:
        ThreadedConnectionPool instance
    """
    global _connection_pool, _connection_string
    conn_str = get_connection_string()
    
    # Reinitialize pool if connection string changed (e.g., port changed)
    if _connection_pool is None or _connection_string != conn_str:
        if _connection_pool is not None:
            # Close existing pool before reinitializing
            try:
                _connection_pool.closeall()
            except Exception:
                pass  # Ignore errors when closing
        _connection_string = conn_str
        _connection_pool = ThreadedConnectionPool(
            minconn=minconn,
            maxconn=maxconn,
            dsn=conn_str
        )
    return _connection_pool


@contextmanager
def get_db_connection():
    """
    Get a database connection from the pool.
    
    Usage:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM agents")
                results = cur.fetchall()
    
    Yields:
        psycopg2.connection: Database connection
    """
    pool = init_connection_pool()
    conn = pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        pool.putconn(conn)


def init_database() -> None:
    """
    Initialize database schema.
    
    Reads and executes specs/database/schema.sql to create all tables.
    """
    from pathlib import Path
    
    # Get project root (assuming this file is in src/chimera_factory/db/)
    project_root = Path(__file__).parent.parent.parent.parent
    schema_path = project_root / "specs" / "database" / "schema.sql"
    
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Execute schema SQL
            cur.execute(schema_sql)
            conn.commit()


def reset_connection_pool() -> None:
    """
    Reset the connection pool (useful for testing or when config changes).
    
    This closes the existing pool and forces reinitialization on next use.
    """
    global _connection_pool, _connection_string
    if _connection_pool is not None:
        try:
            _connection_pool.closeall()
        except Exception:
            pass  # Ignore errors when closing
    _connection_pool = None
    _connection_string = None
    
    # Force reload of environment variables
    from dotenv import load_dotenv
    load_dotenv(override=True)


def test_connection() -> bool:
    """
    Test database connection.
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT version();")
                version = cur.fetchone()
                print(f"✅ Database connected: PostgreSQL {version[0]}")
        return True
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False
