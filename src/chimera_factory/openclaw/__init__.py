"""
OpenClaw Network Integration for Project Chimera.

This module provides integration with the OpenClaw agent social network,
enabling agents to publish capabilities, discover other agents, and collaborate.

Reference: specs/openclaw_integration.md
"""

from .models import (
    AgentStatus,
    AgentCapability,
    AgentResources,
    AgentReputation,
    StatusPublication,
    CapabilityPublication,
    DiscoveryQuery,
    DiscoveryResponse,
    CollaborationRequest,
    CollaborationResponse,
    TrendShare,
)
from .service import OpenClawService
from .status_service import OpenClawStatusService

__all__ = [
    "AgentStatus",
    "AgentCapability",
    "AgentResources",
    "AgentReputation",
    "StatusPublication",
    "CapabilityPublication",
    "DiscoveryQuery",
    "DiscoveryResponse",
    "CollaborationRequest",
    "CollaborationResponse",
    "TrendShare",
    "OpenClawService",
    "OpenClawStatusService",
]
