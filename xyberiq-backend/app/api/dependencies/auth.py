"""Authentication-related dependencies."""

from __future__ import annotations

import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.dependencies import get_db, get_settings_dependency
from app.api.dependencies.tenant import get_current_tenant
from app.core.security import InvalidTokenError, decode_token
from app.db.models import RoleKey, Tenant, User, UserRole


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", scheme_name="Bearer")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    settings = Depends(get_settings_dependency),
    tenant: Tenant = Depends(get_current_tenant),
) -> User:
    try:
        payload = decode_token(token, settings=settings)
    except InvalidTokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    if payload.get("token_type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token required")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")

    tenant_id = payload.get("tenant_id")
    if not tenant_id or str(tenant.id) != str(tenant_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant mismatch")

    stmt = (
        select(User)
        .options(selectinload(User.roles).selectinload(UserRole.role))
        .where(User.id == uuid.UUID(str(user_id)))
    )
    user = db.execute(stmt).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def require_roles(*required_roles: RoleKey):
    async def dependency(user: User = Depends(get_current_user)) -> User:
        user_roles = {user_role.role.key for user_role in user.roles if user_role.role is not None}
        if not set(required_roles).issubset(user_roles):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return user

    return dependency


__all__ = ["oauth2_scheme", "get_current_user", "require_roles"]
