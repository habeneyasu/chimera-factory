"""
Logging and audit trail utilities for Project Chimera.

Reference: specs/_meta.md (100% of agent actions logged)
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chimera_factory.log'),
        logging.StreamHandler()
    ]
)


def setup_logger(name: str) -> logging.Logger:
    """
    Set up a logger for a module.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def log_action(
    action_type: str,
    agent_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    logger: Optional[logging.Logger] = None
) -> None:
    """
    Log an agent action for audit trail.
    
    Reference: specs/_meta.md (100% of agent actions logged)
    
    Args:
        action_type: Type of action (e.g., "trend_research", "content_generate")
        agent_id: Optional agent ID
        details: Optional action details
        logger: Optional logger instance
    """
    if logger is None:
        logger = logging.getLogger("chimera_factory.audit")
    
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "action_type": action_type,
        "agent_id": agent_id,
        "details": details or {}
    }
    
    logger.info(f"ACTION: {json.dumps(log_data)}")


def audit_log(
    event: str,
    agent_id: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """
    Create an audit log entry.
    
    Args:
        event: Event name (e.g., "content_created", "engagement_posted")
        agent_id: Optional agent ID
        resource_type: Optional resource type (e.g., "content", "engagement")
        resource_id: Optional resource ID
        metadata: Optional additional metadata
    """
    logger = logging.getLogger("chimera_factory.audit")
    
    audit_data = {
        "timestamp": datetime.now().isoformat(),
        "event": event,
        "agent_id": agent_id,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "metadata": metadata or {}
    }
    
    logger.info(f"AUDIT: {json.dumps(audit_data)}")
