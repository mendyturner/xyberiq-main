"""Training telemetry models."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric
from sqlalchemy.dialects.postgresql import ENUM, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import (
    Base,
    TenantScopedMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)

from .enums import EventType


class Event(UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin, Base):
    """Audit-friendly user events within the platform."""

    __tablename__ = "events"

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    event_type: Mapped[EventType] = mapped_column(
        ENUM(EventType, name="event_type", create_type=False), nullable=False
    )
    payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    user: Mapped[Optional["User"]] = relationship("User")


class Assessment(UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin, Base):
    """Training assessment attempts."""

    __tablename__ = "assessments"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    module_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("modules.id", ondelete="CASCADE"),
        nullable=False,
    )
    assignment_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assignments.id", ondelete="SET NULL"),
        nullable=True,
    )
    attempt_no: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    answers: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship("User")
    module: Mapped["Module"] = relationship("Module")
    assignment: Mapped[Optional["Assignment"]] = relationship("Assignment")


__all__ = ["Event", "Assessment"]
