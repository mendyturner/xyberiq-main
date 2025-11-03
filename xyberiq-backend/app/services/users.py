"""User service operations."""

from __future__ import annotations

import uuid
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.security import get_password_hash, verify_password
from app.db.models import Role, RoleKey, User, UserRole, UserStatus


class UserService:
    """Encapsulates user-related persistence logic."""

    @staticmethod
    def create_user(
        *,
        db: Session,
        tenant_id: uuid.UUID,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        department: str | None = None,
        title: str | None = None,
        roles: Iterable[RoleKey] | None = None,
        status: UserStatus = UserStatus.ACTIVE,
    ) -> User:
        hashed = get_password_hash(password)
        user = User(
            tenant_id=tenant_id,
            email=email.lower(),
            password_hash=hashed,
            first_name=first_name,
            last_name=last_name,
            department=department,
            title=title,
            status=status,
        )
        db.add(user)
        db.flush()

        if roles:
            UserService.assign_roles(db=db, user_id=user.id, roles=list(roles))

        return user

    @staticmethod
    def assign_roles(*, db: Session, user_id: uuid.UUID, roles: Iterable[RoleKey]) -> None:
        user = db.get(User, user_id)
        if user is None:
            raise ValueError("User not found")

        role_records = (
            db.execute(
                select(Role).where(Role.tenant_id == user.tenant_id, Role.key.in_(list(roles)))
            )
            .scalars()
            .all()
        )
        existing_role_ids = {ur.role_id for ur in user.roles}
        for role in role_records:
            if role.id in existing_role_ids:
                continue
            user_role = UserRole(tenant_id=user.tenant_id, user_id=user.id, role_id=role.id)
            user_role.role = role
            db.add(user_role)
        db.flush()

    @staticmethod
    def authenticate(
        *, db: Session, tenant_id: uuid.UUID, email: str, password: str
    ) -> User | None:
        stmt = (
            select(User)
            .options(selectinload(User.roles).selectinload(UserRole.role))
            .where(User.email == email.lower(), User.tenant_id == tenant_id)
            .execution_options(tenant_aware=False)
        )
        user = db.execute(stmt).scalar_one_or_none()
        if user is None:
            return None
        if user.status != UserStatus.ACTIVE:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    @staticmethod
    def set_password(*, db: Session, user: User, password: str) -> None:
        user.password_hash = get_password_hash(password)
        db.add(user)
        db.flush()


__all__ = ["UserService"]
