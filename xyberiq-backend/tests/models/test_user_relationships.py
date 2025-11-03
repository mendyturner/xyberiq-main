"""Tests for user-manager relationships."""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.db.models import Tenant, User


def create_tenant(db: Session) -> Tenant:
    tenant = Tenant(
        name="Acme",
        slug=f"acme-{uuid.uuid4().hex[:6]}",
        contact_email="ops@acme.test",
    )
    db.add(tenant)
    db.flush()
    return tenant


def create_user(
    db: Session,
    tenant: Tenant,
    email: str,
    manager: User | None = None,
) -> User:
    user = User(
        tenant_id=tenant.id,
        email=email,
        password_hash="hashed",
        first_name="Test",
        last_name="User",
        manager_user_id=manager.id if manager else None,
    )
    db.add(user)
    db.flush()
    return user


def test_deleting_manager_keeps_direct_reports(db_session: Session) -> None:
    tenant = create_tenant(db_session)
    manager = create_user(db_session, tenant, "manager@acme.test")
    report = create_user(db_session, tenant, "employee@acme.test", manager=manager)

    db_session.delete(manager)
    db_session.commit()

    db_session.expire_all()
    remaining = db_session.get(User, report.id)
    assert remaining is not None
    assert remaining.manager_user_id is None
