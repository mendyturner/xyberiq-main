"""Audit log service."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import AuditLog


class AuditService:
    """Utility helpers for writing audit log entries."""

    @staticmethod
    def log(
        *,
        db: Session,
        tenant_id: uuid.UUID,
        action: str,
        actor_user_id: uuid.UUID | None = None,
        target_type: str | None = None,
        target_id: str | None = None,
        ip: str | None = None,
        user_agent: str | None = None,
        meta: dict[str, Any] | None = None,
    ) -> AuditLog:
        entry = AuditLog(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            ip=ip,
            user_agent=user_agent,
            meta=meta,
        )
        db.add(entry)
        db.flush()
        return entry


__all__ = ["AuditService"]
