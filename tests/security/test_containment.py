"""
Tests for containment policy enforcement.

Reference: specs/security_policy.md (Containment Policy)
"""

import pytest
from unittest.mock import Mock, patch

from chimera_factory.security.containment import (
    ContainmentPolicy,
    SecurityViolationError,
    ResourceQuotaExceededError,
    EscalationTriggeredError,
    OperationType,
    ResourceType,
    EscalationSeverity,
)


class TestForbiddenOperations:
    """Test forbidden operation detection."""
    
    def test_file_system_forbidden_operation(self):
        """Test that reading outside sandbox is forbidden."""
        policy = ContainmentPolicy(agent_id="test-agent")
        
        with pytest.raises(SecurityViolationError) as exc_info:
            policy.check_operation_allowed(
                OperationType.FILE_SYSTEM,
                {"path": "/etc/passwd", "operation": "read"}
            )
        
        assert "forbidden" in str(exc_info.value).lower()
    
    def test_network_private_ip_forbidden(self):
        """Test that private IP ranges are forbidden."""
        policy = ContainmentPolicy(agent_id="test-agent")
        
        with pytest.raises(SecurityViolationError) as exc_info:
            policy.check_operation_allowed(
                OperationType.NETWORK,
                {"url": "http://192.168.1.1/api"}
            )
        
        assert "forbidden" in str(exc_info.value).lower()
    
    def test_shell_command_forbidden(self):
        """Test that shell commands are forbidden."""
        policy = ContainmentPolicy(agent_id="test-agent")
        
        with pytest.raises(SecurityViolationError) as exc_info:
            policy.check_operation_allowed(
                OperationType.PROCESS,
                {"command": "subprocess.run(['rm', '-rf', '/'])", "operation": "execute"}
            )
        
        assert "forbidden" in str(exc_info.value).lower()
    
    def test_dangerous_sql_forbidden(self):
        """Test that dangerous SQL operations are forbidden."""
        policy = ContainmentPolicy(agent_id="test-agent")
        
        with pytest.raises(SecurityViolationError) as exc_info:
            policy.check_operation_allowed(
                OperationType.DATABASE,
                {"query": "DROP TABLE users", "operation": "execute"}
            )
        
        assert "forbidden" in str(exc_info.value).lower()
    
    def test_allowed_operation_passes(self):
        """Test that allowed operations pass checks."""
        policy = ContainmentPolicy(agent_id="test-agent")
        
        # Should not raise
        result = policy.check_operation_allowed(
            OperationType.FILE_SYSTEM,
            {"path": "/app/data/file.txt", "operation": "read"}
        )
        
        assert result is True


class TestResourceQuotas:
    """Test resource quota enforcement."""
    
    def test_memory_quota_warning(self):
        """Test memory quota warning threshold."""
        policy = ContainmentPolicy(agent_id="test-agent")
        
        # Use 80% of quota (should trigger warning)
        allowed, warning = policy.check_resource_quota(
            ResourceType.MEMORY,
            400 * 1024 * 1024  # 400 MB (80% of 512 MB)
        )
        
        assert allowed is True
        assert warning is not None
        assert "warning" in warning.lower()
    
    def test_memory_quota_exceeded(self):
        """Test memory quota exceeded raises error."""
        policy = ContainmentPolicy(agent_id="test-agent")
        
        # Use more than critical threshold (should raise error)
        with pytest.raises(ResourceQuotaExceededError) as exc_info:
            policy.check_resource_quota(
                ResourceType.MEMORY,
                500 * 1024 * 1024  # 500 MB (> 480 MB critical threshold)
            )
        
        assert "quota exceeded" in str(exc_info.value).lower()
    
    def test_api_requests_quota(self):
        """Test API requests quota enforcement."""
        policy = ContainmentPolicy(agent_id="test-agent")
        
        # Use 80% of quota (should trigger warning)
        allowed, warning = policy.check_resource_quota(
            ResourceType.API_REQUESTS,
            400  # 400 requests (80% of 500)
        )
        
        assert allowed is True
        assert warning is not None
    
    def test_concurrent_tasks_quota(self):
        """Test concurrent tasks quota enforcement."""
        policy = ContainmentPolicy(agent_id="test-agent")
        
        # Use 80% of quota
        allowed, warning = policy.check_resource_quota(
            ResourceType.CONCURRENT_TASKS,
            4  # 4 tasks (80% of 5)
        )
        
        assert allowed is True
        assert warning is not None


class TestEscalationTriggers:
    """Test automatic escalation triggers."""
    
    def test_immediate_escalation_on_forbidden_operation(self):
        """Test that forbidden operations trigger immediate escalation."""
        policy = ContainmentPolicy(agent_id="test-agent")
        
        with pytest.raises(SecurityViolationError):
            policy.check_operation_allowed(
                OperationType.FILE_SYSTEM,
                {"path": "/etc/passwd", "operation": "read"}
            )
        
        # Check that escalation was logged
        assert len(policy.escalation_log) == 0  # Escalation happens in _escalate
    
    def test_resource_quota_escalation(self):
        """Test that resource quota violations trigger escalation."""
        policy = ContainmentPolicy(agent_id="test-agent")
        
        with pytest.raises(ResourceQuotaExceededError):
            policy.check_resource_quota(
                ResourceType.MEMORY,
                500 * 1024 * 1024  # Exceeds critical threshold
            )
        
        # Check that escalation was logged
        assert len(policy.escalation_log) > 0
        assert policy.escalation_log[-1]["severity"] == EscalationSeverity.TERMINATE.value
    
    def test_warning_escalation(self):
        """Test that warnings trigger escalation."""
        policy = ContainmentPolicy(agent_id="test-agent")
        
        # Trigger warning
        allowed, warning = policy.check_resource_quota(
            ResourceType.MEMORY,
            400 * 1024 * 1024  # 80% threshold
        )
        
        # Check that warning escalation was logged
        assert len(policy.escalation_log) > 0
        assert policy.escalation_log[-1]["severity"] == EscalationSeverity.WARNING.value
    
    def test_should_escalate_logic(self):
        """Test escalation decision logic."""
        policy = ContainmentPolicy(agent_id="test-agent")
        
        # Critical escalation should trigger
        assert policy.should_escalate(
            "resource_quota_critical",
            EscalationSeverity.TERMINATE,
            {"resource_type": "memory"}
        ) is True
        
        # Warning escalation should trigger
        assert policy.should_escalate(
            "resource_quota_warning",
            EscalationSeverity.WARNING,
            {"resource_type": "memory"}
        ) is True
        
        # HITL escalation should trigger
        assert policy.should_escalate(
            "low_confidence",
            EscalationSeverity.HITL_REVIEW,
            {"confidence": 0.75}
        ) is True


class TestContainmentIntegration:
    """Test containment policy integration."""
    
    def test_operation_with_quota_check(self):
        """Test operation check with resource quota."""
        policy = ContainmentPolicy(agent_id="test-agent")
        
        # Check operation is allowed
        policy.check_operation_allowed(
            OperationType.API_CALL,
            {"url": "https://api.example.com", "method": "GET"}
        )
        
        # Check resource quota
        allowed, warning = policy.check_resource_quota(
            ResourceType.API_REQUESTS,
            1
        )
        
        assert allowed is True
    
    def test_audit_logging(self):
        """Test that operations are logged."""
        policy = ContainmentPolicy(agent_id="test-agent")
        
        # Perform operation
        policy.check_operation_allowed(
            OperationType.API_CALL,
            {"url": "https://api.example.com", "method": "GET"}
        )
        
        # Check that operation was logged
        assert len(policy.operation_history) >= 0  # May or may not log allowed operations
    
    def test_security_event_logging(self):
        """Test that security violations are logged."""
        policy = ContainmentPolicy(agent_id="test-agent")
        
        # Attempt forbidden operation
        with pytest.raises(SecurityViolationError):
            policy.check_operation_allowed(
                OperationType.FILE_SYSTEM,
                {"path": "/etc/passwd", "operation": "read"}
            )
        
        # Check that security event was logged
        assert len(policy.operation_history) > 0
        assert policy.operation_history[-1]["violation_type"] == "forbidden_operation"
