"""
Redis caching client for Project Chimera.

Reference: specs/_meta.md (Hybrid Database Architecture - Redis for ephemeral cache)
"""

import os
import json
import redis
from typing import Optional, Any
from dotenv import load_dotenv

load_dotenv()

_redis_client: Optional[redis.Redis] = None


def get_redis_client() -> redis.Redis:
    """
    Get Redis client instance.
    
    Reads configuration from environment variables:
    - REDIS_URL: Full Redis URL (preferred)
    - REDIS_HOST: Redis host (default: localhost)
    - REDIS_PORT: Redis port (default: 6379)
    - REDIS_DB: Redis database number (default: 0)
    
    Returns:
        Redis client
    """
    global _redis_client
    if _redis_client is None:
        # Try full URL first
        redis_url = os.getenv("REDIS_URL")
        if not redis_url:
            # Construct from individual components
            host = os.getenv("REDIS_HOST", "localhost")
            port = os.getenv("REDIS_PORT", "6379")
            db = os.getenv("REDIS_DB", "0")
            redis_url = f"redis://{host}:{port}/{db}"
        _redis_client = redis.from_url(redis_url, decode_responses=True)
    return _redis_client


def cache_key(prefix: str, *args) -> str:
    """
    Generate a cache key.
    
    Args:
        prefix: Key prefix
        *args: Additional key components
        
    Returns:
        Cache key string
    """
    parts = [prefix] + [str(arg) for arg in args]
    return ":".join(parts)


def get_cache(key: str, default: Any = None) -> Optional[Any]:
    """
    Get value from cache.
    
    Args:
        key: Cache key
        default: Default value if key not found
        
    Returns:
        Cached value or default
    """
    try:
        client = get_redis_client()
        value = client.get(key)
        if value is None:
            return default
        # Try to parse as JSON, fallback to string
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    except Exception:
        # If Redis is unavailable, return default
        return default


def set_cache(key: str, value: Any, ttl: int = 3600) -> bool:
    """
    Set value in cache.
    
    Args:
        key: Cache key
        value: Value to cache
        ttl: Time to live in seconds (default: 1 hour)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        client = get_redis_client()
        # Serialize value as JSON if it's not a string
        if isinstance(value, str):
            serialized = value
        else:
            serialized = json.dumps(value)
        client.setex(key, ttl, serialized)
        return True
    except Exception:
        # If Redis is unavailable, silently fail
        return False


def delete_cache(key: str) -> bool:
    """
    Delete key from cache.
    
    Args:
        key: Cache key to delete
        
    Returns:
        True if successful, False otherwise
    """
    try:
        client = get_redis_client()
        client.delete(key)
        return True
    except Exception:
        return False
