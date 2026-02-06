"""
Base API client class to reduce code duplication.

Reference: specs/technical.md (API Contracts)
"""

import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()


class BaseAPIClient:
    """Base class for all API clients with common functionality."""
    
    def __init__(self, api_key_env: str, base_url: str, api_secret_env: Optional[str] = None):
        """
        Initialize base API client.
        
        Args:
            api_key_env: Environment variable name for API key
            base_url: Base URL for the API
            api_secret_env: Optional environment variable name for API secret
        """
        self.api_key = os.getenv(api_key_env)
        self.api_secret = os.getenv(api_secret_env) if api_secret_env else None
        self.base_url = base_url
        self._headers = self._build_headers()
    
    def _build_headers(self) -> Dict[str, str]:
        """Build default headers for API requests."""
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    def is_configured(self) -> bool:
        """Check if the client is properly configured with API credentials."""
        return self.api_key is not None
    
    @property
    def headers(self) -> Dict[str, str]:
        """Get request headers."""
        return self._headers.copy()
