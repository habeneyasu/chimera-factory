# Security Policy: Project Chimera

**Prepared By**: habeneyasu  
**Repository**: [https://github.com/habeneyasu/chimera-factory](https://github.com/habeneyasu/chimera-factory)  
**Last Updated**: February 2026  
**Version**: 1.0.0

---

## Executive Summary

This document defines the **Containment Policy** for Project Chimera agents. The policy establishes explicit forbidden operations, resource quotas, and automatic escalation triggers that agents must enforce as executable checks.

**Security-First Principle**: All agent operations must pass containment checks before execution. Violations trigger automatic escalation and logging.

---

## Containment Policy
,
### 1. Forbidden Operations

The following operations are **explicitly forbidden** and must be blocked by containment checks:

#### 1.1 System-Level Forbidden Operations

- ❌ **File System Access Outside Sandbox**
  - Reading files outside `/app` directory
  - Writing files outside designated output directories
  - Deleting files not created by the agent
  - Accessing system configuration files (`/etc`, `/proc`, `/sys`)

- ❌ **Network Access Restrictions**
  - Direct connections to non-whitelisted domains
  - Outbound connections to private IP ranges (10.x.x.x, 172.16.x.x, 192.168.x.x)
  - Opening listening ports
  - Bypassing MCP protocol for external interactions

- ❌ **Process Execution**
  - Executing shell commands (`subprocess`, `os.system`, `eval`, `exec`)
  - Spawning child processes
  - Installing system packages
  - Modifying system environment variables

- ❌ **Database Operations**
  - DROP TABLE, DROP DATABASE, TRUNCATE operations
  - ALTER TABLE operations without migration approval
  - Direct SQL execution (must use ORM/query builder)
  - Accessing databases outside designated connection pool

#### 1.2 Content-Level Forbidden Operations

- ❌ **Harmful Content Generation**
  - Generating content with explicit violence, hate speech, or illegal activities
  - Creating deepfakes or manipulated media without disclosure
  - Generating content that violates platform terms of service
  - Publishing content without human review when confidence < 0.70

- ❌ **Sensitive Data Exposure**
  - Logging API keys, passwords, or tokens
  - Including secrets in error messages
  - Storing credentials in plain text
  - Transmitting PII without encryption

#### 1.3 Agent Behavior Forbidden Operations

- ❌ **Resource Exhaustion**
  - Infinite loops or recursive calls without limits
  - Memory allocation exceeding quotas
  - CPU usage exceeding time limits
  - Concurrent operations exceeding thread/process limits

- ❌ **Bypassing Safety Mechanisms**
  - Disabling rate limiting
  - Bypassing HITL (Human-in-the-Loop) review
  - Modifying confidence scores
  - Skipping audit logging

---

## 2. Resource Quotas

All agents must operate within the following resource quotas:

### 2.1 API Request Quotas

| Resource | Quota | Window | Escalation Trigger |
|----------|-------|--------|-------------------|
| **Trend Research API Calls** | 100 requests | 1 hour | >80 requests → Log warning |
| **Content Generation API Calls** | 50 requests | 1 hour | >40 requests → Throttle |
| **Engagement API Calls** | 200 requests | 1 hour | >160 requests → Rate limit |
| **OpenClaw Network Calls** | 30 requests | 1 hour | >24 requests → Queue requests |
| **Total API Calls (All Sources)** | 500 requests | 1 hour | >400 requests → Block new requests |

### 2.2 Computational Resource Quotas

| Resource | Quota | Escalation Trigger |
|----------|-------|-------------------|
| **Memory Usage** | 512 MB per agent | >400 MB → Log warning, >480 MB → Kill process |
| **CPU Time** | 60 seconds per task | >45 seconds → Log warning, >55 seconds → Terminate |
| **Concurrent Tasks** | 5 tasks per agent | >4 tasks → Queue new tasks |
| **Database Connections** | 10 connections per agent | >8 connections → Reject new connections |
| **Redis Connections** | 20 connections per agent | >16 connections → Reject new connections |

### 2.3 Storage Quotas

| Resource | Quota | Escalation Trigger |
|----------|-------|-------------------|
| **Content Storage** | 1 GB per agent | >800 MB → Log warning, >950 MB → Block uploads |
| **Log Storage** | 100 MB per agent | >80 MB → Rotate logs, >95 MB → Archive logs |
| **Cache Storage** | 500 MB per agent | >400 MB → Evict LRU, >480 MB → Clear cache |

### 2.4 Time-Based Quotas

| Resource | Quota | Escalation Trigger |
|----------|-------|-------------------|
| **Task Execution Time** | 5 minutes per task | >4 minutes → Log warning, >4.5 minutes → Terminate |
| **API Response Time** | 30 seconds per request | >25 seconds → Log warning, >28 seconds → Timeout |
| **Database Query Time** | 10 seconds per query | >8 seconds → Log warning, >9 seconds → Cancel query |

---

## 3. Automatic Escalation Triggers

Escalation triggers are conditions that automatically invoke safety mechanisms:

### 3.1 Immediate Escalation (Block Operation)

These triggers **immediately block** the operation and log a security event:

1. **Forbidden Operation Detected**
   - Any operation in Section 1 (Forbidden Operations)
   - **Action**: Block operation, log security event, notify security team

2. **Resource Quota Exceeded (Critical)**
   - Memory usage > 480 MB
   - CPU time > 55 seconds
   - Storage > 95% of quota
   - **Action**: Terminate operation, log resource violation, escalate to operations

3. **Authentication Failure (Repeated)**
   - 3+ failed authentication attempts in 5 minutes
   - **Action**: Block agent, require manual re-authentication, log security event

4. **Rate Limit Violation (Severe)**
   - Exceeding quota by >20% (e.g., >120 requests when quota is 100)
   - **Action**: Block all requests for 1 hour, log violation, notify operations

### 3.2 Warning Escalation (Log & Monitor)

These triggers **log warnings** and increase monitoring:

1. **Resource Quota Warning (80% threshold)**
   - Memory usage > 400 MB (80% of 512 MB)
   - API calls > 80% of quota
   - Storage > 80% of quota
   - **Action**: Log warning, increase monitoring frequency, alert operations

2. **Performance Degradation**
   - API response time > 25 seconds
   - Database query time > 8 seconds
   - Task execution time > 4 minutes
   - **Action**: Log performance warning, throttle operations, investigate

3. **Confidence Score Below Threshold**
   - Content generation confidence < 0.70
   - **Action**: Require HITL review, log low confidence event, block auto-approval

### 3.3 Review Escalation (HITL Required)

These triggers **require human review**:

1. **Low Confidence Content**
   - Confidence score 0.70 - 0.90
   - **Action**: Queue for human review, block auto-approval, notify reviewers

2. **Sensitive Topic Detected**
   - Content contains sensitive keywords (politics, finance, health)
   - **Action**: Require mandatory human review, block auto-approval

3. **Unusual Activity Pattern**
   - Agent behavior deviates from normal patterns
   - **Action**: Flag for review, increase monitoring, require approval

---

## 4. Enforcement Implementation

### 4.1 Containment Checks

All agent operations must pass containment checks before execution:

```python
from chimera_factory.security.containment import ContainmentPolicy

# Before executing any operation
containment = ContainmentPolicy(agent_id="agent-123")
if not containment.check_operation_allowed(operation_type, operation_params):
    raise SecurityViolationError("Operation forbidden by containment policy")

# Check resource quotas
if not containment.check_resource_quota(resource_type, amount):
    raise ResourceQuotaExceededError("Resource quota exceeded")
```

### 4.2 Automatic Escalation

Escalation triggers are implemented as enforceable checks:

```python
# Automatic escalation on trigger
if containment.should_escalate(trigger_type, severity):
    containment.escalate(
        trigger=trigger_type,
        severity=severity,
        action=escalation_action,
        context=operation_context
    )
```

### 4.3 Audit Logging

All containment checks and escalations are logged:

- **Security Events**: Logged to security audit log
- **Resource Violations**: Logged to operations log
- **Escalations**: Logged to escalation log with full context

---

## 5. Compliance Requirements

### 5.1 Mandatory Checks

The following checks are **mandatory** and cannot be bypassed:

1. ✅ Forbidden operation check (before every operation)
2. ✅ Resource quota check (before resource allocation)
3. ✅ Escalation trigger check (after operation completion)
4. ✅ Audit log entry (for all operations)

### 5.2 Testing Requirements

Containment policy must be tested:

- ✅ Unit tests for all forbidden operations
- ✅ Unit tests for all resource quotas
- ✅ Unit tests for all escalation triggers
- ✅ Integration tests for enforcement mechanisms
- ✅ E2E tests for complete containment workflow

---

## 6. References

- **Spec-Driven Development**: `specs/_meta.md` (Security constraints)
- **Technical Specifications**: `specs/technical.md` (Rate limiting, authentication)
- **Implementation**: `src/chimera_factory/security/containment.py`
- **Tests**: `tests/security/test_containment.py`

---

**This policy is enforced programmatically. All agents must pass containment checks before executing operations.**
