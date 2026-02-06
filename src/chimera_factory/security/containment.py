"""
Containment Policy Implementation for Project Chimera.

This module implements the security containment policy with:
- Explicit forbidden operations
- Resource quotas
- Automatic escalation triggers

Reference: specs/security_policy.md (Containment Policy)
"""

import os
import time
import logging
from enum import Enum
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from uuid import UUID

from chimera_factory.exceptions import (
    ChimeraError,
    SecurityViolationError,
    ResourceQuotaExceededError,
    EscalationTriggeredError,
)

logger = logging.getLogger(__name__)


class OperationType(Enum):
    """Types of operations that can be checked."""
    FILE_SYSTEM = "file_system"
    NETWORK = "network"
    PROCESS = "process"
    DATABASE = "database"
    CONTENT_GENERATION = "content_generation"
    API_CALL = "api_call"
    SKILL_EXECUTION = "skill_execution"


class ResourceType(Enum):
    """Types of resources that have quotas."""
    MEMORY = "memory"
    CPU_TIME = "cpu_time"
    API_REQUESTS = "api_requests"
    STORAGE = "storage"
    DATABASE_CONNECTIONS = "database_connections"
    REDIS_CONNECTIONS = "redis_connections"
    CONCURRENT_TASKS = "concurrent_tasks"


class EscalationSeverity(Enum):
    """Severity levels for escalations."""
    WARNING = "warning"
    BLOCK = "block"
    TERMINATE = "terminate"
    HITL_REVIEW = "hitl_review"


@dataclass
class ResourceQuota:
    """Resource quota definition."""
    resource_type: ResourceType
    max_amount: float
    warning_threshold: float = 0.8  # 80% of max
    critical_threshold: float = 0.95  # 95% of max
    window_seconds: Optional[int] = None  # For time-based quotas


@dataclass
class EscalationTrigger:
    """Escalation trigger definition."""
    trigger_name: str
    condition: str  # Python expression to evaluate
    severity: EscalationSeverity
    action: str  # Action to take when triggered
    log_message: str


# Security exceptions are defined in exceptions.py to avoid circular imports


class ContainmentPolicy:
    """
    Containment policy enforcement for agent operations.
    
    Implements:
    - Forbidden operation checks
    - Resource quota enforcement
    - Automatic escalation triggers
    
    Reference: specs/security_policy.md
    """
    
    # Forbidden operations (from specs/security_policy.md Section 1)
    FORBIDDEN_OPERATIONS = {
        # File system
        "read_outside_sandbox": ["/etc", "/proc", "/sys", "/root"],
        "write_outside_sandbox": ["/etc", "/proc", "/sys", "/root"],
        "delete_system_files": ["/etc", "/proc", "/sys", "/root"],
        
        # Network
        "private_ip_ranges": ["10.", "172.16.", "192.168."],
        "non_whitelisted_domains": [],  # Populated from config
        
        # Process
        "shell_commands": ["subprocess", "os.system", "eval", "exec"],
        "package_installation": ["apt-get", "pip install", "npm install"],
        
        # Database
        "dangerous_sql": ["DROP TABLE", "DROP DATABASE", "TRUNCATE", "ALTER TABLE"],
    }
    
    # Resource quotas (from specs/security_policy.md Section 2)
    RESOURCE_QUOTAS: Dict[ResourceType, ResourceQuota] = {
        ResourceType.MEMORY: ResourceQuota(
            resource_type=ResourceType.MEMORY,
            max_amount=512 * 1024 * 1024,  # 512 MB
            warning_threshold=0.8,  # 400 MB
            critical_threshold=0.9375,  # 480 MB
        ),
        ResourceType.CPU_TIME: ResourceQuota(
            resource_type=ResourceType.CPU_TIME,
            max_amount=60,  # 60 seconds
            warning_threshold=0.75,  # 45 seconds
            critical_threshold=0.916,  # 55 seconds
        ),
        ResourceType.API_REQUESTS: ResourceQuota(
            resource_type=ResourceType.API_REQUESTS,
            max_amount=500,  # 500 requests per hour
            warning_threshold=0.8,  # 400 requests
            critical_threshold=0.8,  # 400 requests (block at 80%)
            window_seconds=3600,  # 1 hour
        ),
        ResourceType.STORAGE: ResourceQuota(
            resource_type=ResourceType.STORAGE,
            max_amount=1 * 1024 * 1024 * 1024,  # 1 GB
            warning_threshold=0.8,  # 800 MB
            critical_threshold=0.95,  # 950 MB
        ),
        ResourceType.DATABASE_CONNECTIONS: ResourceQuota(
            resource_type=ResourceType.DATABASE_CONNECTIONS,
            max_amount=10,
            warning_threshold=0.8,  # 8 connections
            critical_threshold=0.8,  # 8 connections
        ),
        ResourceType.REDIS_CONNECTIONS: ResourceQuota(
            resource_type=ResourceType.REDIS_CONNECTIONS,
            max_amount=20,
            warning_threshold=0.8,  # 16 connections
            critical_threshold=0.8,  # 16 connections
        ),
        ResourceType.CONCURRENT_TASKS: ResourceQuota(
            resource_type=ResourceType.CONCURRENT_TASKS,
            max_amount=5,
            warning_threshold=0.8,  # 4 tasks
            critical_threshold=0.8,  # 4 tasks
        ),
    }
    
    def __init__(self, agent_id: str):
        """
        Initialize containment policy for an agent.
        
        Args:
            agent_id: Unique identifier for the agent
        """
        self.agent_id = agent_id
        self.resource_usage: Dict[ResourceType, float] = {}
        self.operation_history: List[Dict[str, Any]] = []
        self.escalation_log: List[Dict[str, Any]] = []
        
    def check_operation_allowed(
        self,
        operation_type: OperationType,
        operation_params: Dict[str, Any]
    ) -> bool:
        """
        Check if an operation is allowed by containment policy.
        
        Args:
            operation_type: Type of operation
            operation_params: Parameters for the operation
            
        Returns:
            True if operation is allowed, False otherwise
            
        Raises:
            SecurityViolationError: If operation is forbidden
        """
        # Check forbidden operations
        if self._is_forbidden_operation(operation_type, operation_params):
            violation = {
                "agent_id": self.agent_id,
                "operation_type": operation_type.value,
                "operation_params": operation_params,
                "timestamp": time.time(),
                "violation_type": "forbidden_operation",
            }
            self._log_security_event(violation)
            raise SecurityViolationError(
                f"Forbidden operation detected: {operation_type.value}. "
                f"Reference: specs/security_policy.md Section 1"
            )
        
        return True
    
    def check_resource_quota(
        self,
        resource_type: ResourceType,
        amount: float
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if resource usage is within quota.
        
        Args:
            resource_type: Type of resource
            amount: Amount of resource to use
            
        Returns:
            Tuple of (is_allowed, warning_message)
            
        Raises:
            ResourceQuotaExceededError: If quota is exceeded
        """
        quota = self.RESOURCE_QUOTAS.get(resource_type)
        if not quota:
            logger.warning(f"No quota defined for {resource_type}")
            return True, None
        
        current_usage = self.resource_usage.get(resource_type, 0.0)
        new_usage = current_usage + amount
        
        # Check critical threshold
        if new_usage > (quota.max_amount * quota.critical_threshold):
            violation = {
                "agent_id": self.agent_id,
                "resource_type": resource_type.value,
                "current_usage": current_usage,
                "requested_amount": amount,
                "quota_max": quota.max_amount,
                "threshold": quota.critical_threshold,
                "timestamp": time.time(),
            }
            self._log_resource_violation(violation)
            self._escalate(
                trigger="resource_quota_critical",
                severity=EscalationSeverity.TERMINATE,
                context=violation
            )
            raise ResourceQuotaExceededError(
                f"Resource quota exceeded (critical): {resource_type.value}. "
                f"Usage: {new_usage}/{quota.max_amount}. "
                f"Reference: specs/security_policy.md Section 2"
            )
        
        # Check warning threshold
        warning = None
        if new_usage > (quota.max_amount * quota.warning_threshold):
            warning = (
                f"Resource quota warning: {resource_type.value} at "
                f"{new_usage/quota.max_amount*100:.1f}% of quota"
            )
            logger.warning(f"[{self.agent_id}] {warning}")
            self._escalate(
                trigger="resource_quota_warning",
                severity=EscalationSeverity.WARNING,
                context={
                    "agent_id": self.agent_id,
                    "resource_type": resource_type.value,
                    "usage_percent": new_usage / quota.max_amount * 100,
                }
            )
        
        # Update usage
        self.resource_usage[resource_type] = new_usage
        
        return True, warning
    
    def should_escalate(
        self,
        trigger_type: str,
        severity: EscalationSeverity,
        context: Dict[str, Any]
    ) -> bool:
        """
        Check if escalation should be triggered.
        
        Args:
            trigger_type: Type of escalation trigger
            severity: Severity level
            context: Context information
            
        Returns:
            True if escalation should occur
        """
        # Immediate escalation for critical triggers
        if severity in [EscalationSeverity.TERMINATE, EscalationSeverity.BLOCK]:
            return True
        
        # Warning escalation
        if severity == EscalationSeverity.WARNING:
            return True
        
        # HITL review escalation
        if severity == EscalationSeverity.HITL_REVIEW:
            return True
        
        return False
    
    def _escalate(
        self,
        trigger: str,
        severity: EscalationSeverity,
        context: Dict[str, Any]
    ) -> None:
        """
        Execute escalation action.
        
        Args:
            trigger: Trigger name
            severity: Severity level
            context: Context information
        """
        escalation = {
            "agent_id": self.agent_id,
            "trigger": trigger,
            "severity": severity.value,
            "context": context,
            "timestamp": time.time(),
        }
        
        self.escalation_log.append(escalation)
        
        # Log escalation
        if severity == EscalationSeverity.TERMINATE:
            logger.critical(
                f"[{self.agent_id}] ESCALATION: {trigger} - TERMINATE operation"
            )
        elif severity == EscalationSeverity.BLOCK:
            logger.error(
                f"[{self.agent_id}] ESCALATION: {trigger} - BLOCK operation"
            )
        elif severity == EscalationSeverity.WARNING:
            logger.warning(
                f"[{self.agent_id}] ESCALATION: {trigger} - WARNING"
            )
        elif severity == EscalationSeverity.HITL_REVIEW:
            logger.info(
                f"[{self.agent_id}] ESCALATION: {trigger} - HITL REVIEW REQUIRED"
            )
        
        # Raise exception for critical escalations
        if severity in [EscalationSeverity.TERMINATE, EscalationSeverity.BLOCK]:
            raise EscalationTriggeredError(
                f"Escalation triggered: {trigger} (severity: {severity.value}). "
                f"Reference: specs/security_policy.md Section 3"
            )
    
    def _is_forbidden_operation(
        self,
        operation_type: OperationType,
        operation_params: Dict[str, Any]
    ) -> bool:
        """Check if operation is in forbidden list."""
        # File system checks
        if operation_type == OperationType.FILE_SYSTEM:
            path = operation_params.get("path", "")
            if any(forbidden in path for forbidden in self.FORBIDDEN_OPERATIONS["read_outside_sandbox"]):
                return True
        
        # Network checks
        if operation_type == OperationType.NETWORK:
            url = operation_params.get("url", "")
            # Check private IP ranges
            if any(url.startswith(prefix) for prefix in self.FORBIDDEN_OPERATIONS["private_ip_ranges"]):
                return True
        
        # Process checks
        if operation_type == OperationType.PROCESS:
            command = operation_params.get("command", "")
            if any(cmd in command for cmd in self.FORBIDDEN_OPERATIONS["shell_commands"]):
                return True
        
        # Database checks
        if operation_type == OperationType.DATABASE:
            query = operation_params.get("query", "")
            if any(sql in query.upper() for sql in self.FORBIDDEN_OPERATIONS["dangerous_sql"]):
                return True
        
        return False
    
    def _log_security_event(self, event: Dict[str, Any]) -> None:
        """Log security event."""
        logger.critical(
            f"SECURITY EVENT: {event['violation_type']} by agent {event['agent_id']}",
            extra=event
        )
        self.operation_history.append(event)
    
    def _log_resource_violation(self, violation: Dict[str, Any]) -> None:
        """Log resource violation."""
        logger.error(
            f"RESOURCE VIOLATION: {violation['resource_type']} by agent {violation['agent_id']}",
            extra=violation
        )
        self.operation_history.append(violation)
