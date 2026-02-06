"""
Custom exceptions for Project Chimera.

Reference: .cursor/rules (Error Handling section)
"""


class ChimeraError(Exception):
    """Base exception for all Chimera Factory errors."""
    
    def __init__(self, message: str, code: str = None, retryable: bool = False):
        """
        Initialize Chimera error.
        
        Args:
            message: Error message
            code: Error code for programmatic handling
            retryable: Whether the operation can be retried
        """
        super().__init__(message)
        self.message = message
        self.code = code
        self.retryable = retryable


class SkillError(ChimeraError):
    """Base exception for skill execution errors."""
    pass


class TrendResearchError(SkillError):
    """Error during trend research."""
    pass


class ContentGenerationError(SkillError):
    """Error during content generation."""
    pass


class EngagementError(SkillError):
    """Error during engagement management."""
    pass


class DatabaseError(ChimeraError):
    """Error during database operations."""
    pass


class RateLimitError(ChimeraError):
    """Error when rate limit is exceeded."""
    
    def __init__(self, platform: str, remaining: int = 0):
        """
        Initialize rate limit error.
        
        Args:
            platform: Platform name
            remaining: Remaining requests in window
        """
        message = f"Rate limit exceeded for {platform}. Remaining: {remaining}"
        super().__init__(message, code="RATE_LIMIT_EXCEEDED", retryable=True)
        self.platform = platform
        self.remaining = remaining


class APIError(ChimeraError):
    """Error during API calls."""
    
    def __init__(self, message: str, platform: str = None, status_code: int = None):
        """
        Initialize API error.
        
        Args:
            message: Error message
            platform: Platform name
            status_code: HTTP status code if applicable
        """
        super().__init__(message, code="API_ERROR", retryable=True)
        self.platform = platform
        self.status_code = status_code


class ValidationError(ChimeraError):
    """Error during input validation."""
    
    def __init__(self, message: str, field: str = None):
        """
        Initialize validation error.
        
        Args:
            message: Error message
            field: Field name that failed validation
        """
        super().__init__(message, code="VALIDATION_ERROR", retryable=False)
        self.field = field
