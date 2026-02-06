"""
Security module for Project Chimera.

Reference: specs/security_policy.md (Containment Policy)
"""

from chimera_factory.security.containment import ContainmentPolicy
from chimera_factory.exceptions import (
    SecurityViolationError,
    ResourceQuotaExceededError,
    EscalationTriggeredError,
)

__all__ = [
    "ContainmentPolicy",
    "SecurityViolationError",
    "ResourceQuotaExceededError",
    "EscalationTriggeredError",
]
