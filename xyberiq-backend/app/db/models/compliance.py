"""Compliance-related models."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ENUM, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

from .enums import ContentType, ControlType


class ComplianceFramework(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Top-level compliance frameworks (HIPAA, SOC2, etc.)."""

    __tablename__ = "compliance_frameworks"
    __table_args__ = (UniqueConstraint("key", name="uq_frameworks_key"),)

    key: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    controls: Mapped[list["Control"]] = relationship("Control", back_populates="framework")
    modules: Mapped[list["Module"]] = relationship("Module", back_populates="framework")


class Control(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Individual controls within a framework."""

    __tablename__ = "controls"
    __table_args__ = (
        UniqueConstraint("framework_id", "control_key", name="uq_controls_framework_key"),
    )

    framework_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("compliance_frameworks.id", ondelete="CASCADE"),
        nullable=False,
    )
    control_key: Mapped[str] = mapped_column(String(128), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    control_type: Mapped[ControlType] = mapped_column(
        ENUM(ControlType, name="control_type", create_type=False), nullable=False
    )
    tags: Mapped[dict | list | None] = mapped_column(
        JSONB, nullable=True, default=list
    )

    framework: Mapped[ComplianceFramework] = relationship(
        "ComplianceFramework", back_populates="controls"
    )
    modules: Mapped[list["ModuleControl"]] = relationship(
        "ModuleControl", back_populates="control"
    )


class Module(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Training modules aligned to frameworks and controls."""

    __tablename__ = "modules"
    __table_args__ = (UniqueConstraint("code", name="uq_modules_code"),)

    framework_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("compliance_frameworks.id", ondelete="SET NULL"),
        nullable=True,
    )
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    difficulty: Mapped[str | None] = mapped_column(String(50), nullable=True)
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    framework: Mapped[ComplianceFramework | None] = relationship(
        "ComplianceFramework", back_populates="modules"
    )
    controls: Mapped[list["ModuleControl"]] = relationship(
        "ModuleControl", back_populates="module"
    )
    contents: Mapped[list["TrainingContent"]] = relationship(
        "TrainingContent", back_populates="module"
    )


class ModuleControl(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Association between modules and controls."""

    __tablename__ = "module_controls"
    __table_args__ = (
        UniqueConstraint("module_id", "control_id", name="uq_module_controls_unique"),
    )

    module_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("modules.id", ondelete="CASCADE"),
        nullable=False,
    )
    control_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("controls.id", ondelete="CASCADE"),
        nullable=False,
    )

    module: Mapped[Module] = relationship("Module", back_populates="controls")
    control: Mapped[Control] = relationship("Control", back_populates="modules")


class TrainingContent(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Training content metadata stored in S3-compatible storage."""

    __tablename__ = "training_content"
    __table_args__ = (
        UniqueConstraint("module_id", "version", name="uq_content_module_version"),
    )

    module_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("modules.id", ondelete="CASCADE"),
        nullable=False,
    )
    version: Mapped[str] = mapped_column(String(64), nullable=False)
    uri: Mapped[str] = mapped_column(String(1024), nullable=False)
    content_type: Mapped[ContentType] = mapped_column(
        ENUM(ContentType, name="content_type", create_type=False), nullable=False
    )
    checksum: Mapped[str | None] = mapped_column(String(128), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    is_published: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )

    module: Mapped[Module] = relationship("Module", back_populates="contents")


__all__ = [
    "ComplianceFramework",
    "Control",
    "Module",
    "ModuleControl",
    "TrainingContent",
]
