"""
Rate limiting utilities for Project Chimera.

Reference: specs/technical.md (Rate Limiting requirements)
"""

import time
from typing import Optional
from chimera_factory.cache import get_cache, set_cache, cache_key


class RateLimiter:
    """
    Rate limiter using token bucket algorithm with Redis cache.
    
    Reference: specs/technical.md (Platform-specific rate limits)
    """
    
    def __init__(self, max_requests: int, window_seconds: int, platform: str = "default"):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds
            platform: Platform identifier for rate limit key
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.platform = platform
    
    def is_allowed(self, identifier: str) -> tuple[bool, Optional[int]]:
        """
        Check if request is allowed.
        
        Args:
            identifier: Unique identifier (e.g., agent_id, API key)
            
        Returns:
            Tuple of (is_allowed, remaining_requests)
        """
        key = cache_key("rate_limit", self.platform, identifier)
        current_time = int(time.time())
        window_start = current_time - self.window_seconds
        
        # Get current request count
        requests = get_cache(key, [])
        if not isinstance(requests, list):
            requests = []
        
        # Remove old requests outside window
        requests = [req_time for req_time in requests if req_time > window_start]
        
        # Check if limit exceeded
        if len(requests) >= self.max_requests:
            return False, 0
        
        # Add current request
        requests.append(current_time)
        set_cache(key, requests, ttl=self.window_seconds)
        
        remaining = self.max_requests - len(requests)
        return True, remaining


# Platform-specific rate limits (from specs/technical.md)
PLATFORM_RATE_LIMITS = {
    "twitter": RateLimiter(max_requests=300, window_seconds=900),  # 300 per 15 min
    "instagram": RateLimiter(max_requests=200, window_seconds=3600),  # 200 per hour
    "tiktok": RateLimiter(max_requests=100, window_seconds=3600),  # 100 per hour
    "threads": RateLimiter(max_requests=300, window_seconds=900),  # 300 per 15 min
    "default": RateLimiter(max_requests=100, window_seconds=3600),  # 100 per hour
}


def check_rate_limit(platform: str, identifier: str) -> tuple[bool, Optional[int]]:
    """
    Check rate limit for a platform.
    
    Args:
        platform: Platform name
        identifier: Unique identifier
        
    Returns:
        Tuple of (is_allowed, remaining_requests)
    """
    limiter = PLATFORM_RATE_LIMITS.get(platform, PLATFORM_RATE_LIMITS["default"])
    return limiter.is_allowed(identifier)
