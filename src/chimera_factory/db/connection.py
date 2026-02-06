"""
Database connection management for Project Chimera.

Reference: specs/database/schema.sql
"""

import os
from psycopg2.pool import ThreadedConnectionPool
from typing import Optional
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

# Connection pool (initialized on first use)
_connection_pool: Optional[ThreadedConnectionPool] = None


def get_connection_string() -> str:
    """
    Get PostgreSQL connection string from environment variables.
    
    Reads from POSTGRES_CONNECTION_STRING or constructs from individual
    POSTGRES_* environment variables.
    
    Environment variables:
    - POSTGRES_CONNECTION_STRING: Full connection string (preferred)
    - POSTGRES_HOST: Database host (default: localhost)
    - POSTGRES_PORT: Database port (default: 5432)
    - POSTGRES_DB: Database name (default: chimera_dev)
    - POSTGRES_USER: Database user (default: postgres)
    - POSTGRES_PASSWORD: Database password (required)
    
    Returns:
        Connection string in format: postgresql://user:password@host:port/database
        
    Raises:
        ValueError: If required environment variables are missing
    """
    # Try full connection string first
    conn_str = os.getenv("POSTGRES_CONNECTION_STRING")
    if conn_str:
        return conn_str
    
    # Construct from individual variables
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
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
    
    return f"postgresql://{user}:{encoded_password}@{host}:{port}/{database}"


def init_connection_pool(minconn: int = 1, maxconn: int = 10) -> ThreadedConnectionPool:
    """
    Initialize database connection pool.
    
    Args:
        minconn: Minimum number of connections
        maxconn: Maximum number of connections
        
    Returns:
        ThreadedConnectionPool instance
    """
    global _connection_pool
    if _connection_pool is None:
        conn_str = get_connection_string()
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
