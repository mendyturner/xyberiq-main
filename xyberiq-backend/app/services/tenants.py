"""Tenant service operations."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Role, RoleKey, Tenant


class TenantService:
    """Service class encapsulating tenant related operations."""

    @staticmethod
    def create_tenant(*, db: Session, name: str, slug: str, contact_email: str) -> Tenant:
        tenant = Tenant(name=name, slug=slug, contact_email=contact_email)
        db.add(tenant)
        db.flush()
        TenantService._ensure_default_roles(db=db, tenant_id=tenant.id)
        return tenant

    @staticmethod
    def _ensure_default_roles(*, db: Session, tenant_id: uuid.UUID) -> None:
        existing = {
            role.key for role in db.execute(
                select(Role).where(Role.tenant_id == tenant_id)
            ).scalars()
        }
        for role_key in RoleKey:
            if role_key in existing:
                continue
            db.add(
                Role(
                    tenant_id=tenant_id,
                    key=role_key,
                    name=role_key.value.title(),
                )
            )
        db.flush()

    @staticmethod
    def get_by_slug(*, db: Session, slug: str) -> Tenant | None:
        stmt = (
            select(Tenant)
            .execution_options(tenant_aware=False)
            .where(Tenant.slug == slug)
        )
        return db.execute(stmt).scalar_one_or_none()


__all__ = ["TenantService"]
