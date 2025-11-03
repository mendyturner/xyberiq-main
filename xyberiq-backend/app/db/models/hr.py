"""HR-related models such as assignments and policies."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    Index,
)
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import (
    Base,
    SoftDeleteMixin,
    TenantScopedMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)

from .enums import AssignmentStatus, PolicyStatus


class Assignment(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    TenantScopedMixin,
    SoftDeleteMixin,
    Base,
):
    """Training assignments for users."""

    __tablename__ = "assignments"
    __table_args__ = (
        Index("ix_assignments_status", "status"),
        Index("ix_assignments_due_date", "due_date"),
    )

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
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[AssignmentStatus] = mapped_column(
        ENUM(AssignmentStatus, name="assignment_status", create_type=False),
        nullable=False,
        default=AssignmentStatus.ASSIGNED,
        server_default=AssignmentStatus.ASSIGNED.value,
    )
    score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    assigned_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    retrain_flag: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )

    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], backref="assignments")
    module: Mapped["Module"] = relationship("Module")
    assigned_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[assigned_by_user_id])


class Policy(UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin, SoftDeleteMixin, Base):
    """Tenant policy documents."""

    __tablename__ = "policies"
    __table_args__ = (
        UniqueConstraint("tenant_id", "name", "version", name="uq_policies_tenant_name_version"),
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str] = mapped_column(String(64), nullable=False)
    uri: Mapped[str] = mapped_column(String(1024), nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[PolicyStatus] = mapped_column(
        ENUM(PolicyStatus, name="policy_status", create_type=False),
        nullable=False,
        default=PolicyStatus.DRAFT,
        server_default=PolicyStatus.DRAFT.value,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    acknowledgements: Mapped[list["PolicyAcknowledgement"]] = relationship(
        "PolicyAcknowledgement", back_populates="policy"
    )


class PolicyAcknowledgement(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    TenantScopedMixin,
    Base,
):
    """Records of users acknowledging policies."""

    __tablename__ = "policy_acknowledgements"
    __table_args__ = (
        UniqueConstraint("tenant_id", "policy_id", "user_id", name="uq_policy_ack_unique"),
    )

    policy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("policies.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    acknowledged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    policy: Mapped[Policy] = relationship("Policy", back_populates="acknowledgements")
    user: Mapped["User"] = relationship("User")


__all__ = ["Assignment", "Policy", "PolicyAcknowledgement"]
