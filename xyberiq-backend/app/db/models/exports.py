"""Data export models."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin, Base

from .enums import ExportStatus, ExportType


class Export(UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin, Base):
    """Exports requested by tenants."""

    __tablename__ = "exports"

    type: Mapped[ExportType] = mapped_column(
        ENUM(ExportType, name="export_type", create_type=False), nullable=False
    )
    status: Mapped[ExportStatus] = mapped_column(
        ENUM(ExportStatus, name="export_status", create_type=False),
        nullable=False,
        default=ExportStatus.PENDING,
        server_default=ExportStatus.PENDING.value,
    )
    storage_uri: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    requested_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    requested_by: Mapped[Optional["User"]] = relationship("User")


__all__ = ["Export"]
