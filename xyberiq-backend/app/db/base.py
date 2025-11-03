"""SQLAlchemy base models and mixins."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, MetaData, func, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)


class Base(DeclarativeBase):
    """Declarative base with shared metadata."""

    metadata = metadata
    type_annotation_map = {
        uuid.UUID: UUID(as_uuid=True),
        dict: JSONB,
    }


class UUIDPrimaryKeyMixin:
    """Provide a UUID primary key column."""

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )


class TimestampMixin:
    """Provide created/updated timestamp columns."""

    @declared_attr.directive
    def created_at(cls) -> Mapped[datetime]:  # noqa: N805 - SQLAlchemy convention
        return mapped_column(
            DateTime(timezone=True),
            default=func.now(),
            server_default=func.now(),
            nullable=False,
        )

    @declared_attr.directive
    def updated_at(cls) -> Mapped[datetime]:  # noqa: N805 - SQLAlchemy convention
        return mapped_column(
            DateTime(timezone=True),
            default=func.now(),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        )


class SoftDeleteMixin:
    """Provide a nullable deleted_at column for soft deletes."""

    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class TenantScopedMixin:
    """Enforce tenant scoping with a tenant_id column."""

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )


__all__ = [
    "Base",
    "metadata",
    "UUIDPrimaryKeyMixin",
    "TimestampMixin",
    "SoftDeleteMixin",
    "TenantScopedMixin",
]
