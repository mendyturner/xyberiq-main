"""Tenant and user related models."""

from __future__ import annotations

import uuid

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import Optional

from app.db.base import (
    Base,
    SoftDeleteMixin,
    TenantScopedMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)

from .enums import RoleKey, UserStatus


class Tenant(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """Represents an organisation tenant."""

    __tablename__ = "tenants"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    contact_email: Mapped[str] = mapped_column(String(255), nullable=False)

    users: Mapped[list["User"]] = relationship("User", back_populates="tenant")
    roles: Mapped[list["Role"]] = relationship("Role", back_populates="tenant")


class Role(UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin, Base):
    """Role definitions per tenant."""

    __tablename__ = "roles"
    __table_args__ = (
        UniqueConstraint("tenant_id", "key", name="uq_roles_tenant_key"),
    )

    key: Mapped[RoleKey] = mapped_column(
        ENUM(RoleKey, name="role_key", create_type=False),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    tenant: Mapped[Tenant] = relationship("Tenant", back_populates="roles")
    users: Mapped[list["UserRole"]] = relationship("UserRole", back_populates="role")


class User(UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin, SoftDeleteMixin, Base):
    """User within a tenant."""

    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("tenant_id", "email", name="uq_users_tenant_email"),
        Index("ix_users_status", "status"),
    )

    email: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_name: Mapped[str] = mapped_column(String(255), nullable=False)
    department: Mapped[str | None] = mapped_column(String(255), nullable=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[UserStatus] = mapped_column(
        ENUM(UserStatus, name="user_status", create_type=False),
        nullable=False,
        default=UserStatus.ACTIVE,
        server_default=UserStatus.ACTIVE.value,
    )
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    manager_user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    tenant: Mapped[Tenant] = relationship("Tenant", back_populates="users")
    manager: Mapped[Optional["User"]] = relationship(
        "User", remote_side="User.id", back_populates="direct_reports"
    )
    direct_reports: Mapped[list["User"]] = relationship(
        "User", back_populates="manager", cascade="all,delete"
    )
    roles: Mapped[list["UserRole"]] = relationship("UserRole", back_populates="user")


class UserRole(UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin, Base):
    """Join table linking users to roles."""

    __tablename__ = "user_roles"
    __table_args__ = (
        UniqueConstraint("tenant_id", "user_id", "role_id", name="uq_user_roles_unique"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"), nullable=False
    )

    user: Mapped[User] = relationship("User", back_populates="roles")
    role: Mapped[Role] = relationship("Role", back_populates="users")


__all__ = ["Tenant", "User", "Role", "UserRole"]
