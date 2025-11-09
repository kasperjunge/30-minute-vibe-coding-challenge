"""Audit logging service for tracking critical actions."""

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def log_action(
    user_id: int,
    action: str,
    entity_type: str,
    entity_id: int,
    details: Optional[Dict[str, Any]],
    db: Session,
) -> AuditLog:
    """
    Log a critical action to the audit log.

    Args:
        user_id: ID of the user performing the action
        action: Action performed (e.g., "approve", "reject", "create_project")
        entity_type: Type of entity affected (e.g., "travel_request", "project")
        entity_id: ID of the entity affected
        details: Additional details about the action (stored as JSON)
        db: Database session

    Returns:
        The created AuditLog entry
    """
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details or {},
        timestamp=datetime.utcnow(),
    )

    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)

    return audit_log


def get_audit_logs_for_entity(
    entity_type: str,
    entity_id: int,
    db: Session,
) -> list[AuditLog]:
    """
    Get all audit logs for a specific entity.

    Args:
        entity_type: Type of entity (e.g., "travel_request", "project")
        entity_id: ID of the entity
        db: Database session

    Returns:
        List of audit log entries for the entity, ordered by timestamp
    """
    return (
        db.query(AuditLog)
        .filter(
            AuditLog.entity_type == entity_type,
            AuditLog.entity_id == entity_id,
        )
        .order_by(AuditLog.timestamp.desc())
        .all()
    )


def get_audit_logs_by_user(
    user_id: int,
    db: Session,
    limit: Optional[int] = None,
) -> list[AuditLog]:
    """
    Get all audit logs for actions performed by a specific user.

    Args:
        user_id: ID of the user
        db: Database session
        limit: Optional limit on number of results

    Returns:
        List of audit log entries for the user, ordered by timestamp
    """
    query = db.query(AuditLog).filter(AuditLog.user_id == user_id).order_by(AuditLog.timestamp.desc())

    if limit:
        query = query.limit(limit)

    return query.all()


def get_recent_audit_logs(
    db: Session,
    limit: int = 100,
) -> list[AuditLog]:
    """
    Get recent audit logs across all users and entities.

    Args:
        db: Database session
        limit: Maximum number of entries to return (default: 100)

    Returns:
        List of recent audit log entries, ordered by timestamp
    """
    return db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()
