"""Authentication service helpers."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from redis import Redis
from app.core.config import Settings
from app.core.security import (
    InvalidTokenError,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.db.models import Tenant, User


REFRESH_TOKEN_PREFIX = "auth:refresh:"
RESET_TOKEN_PREFIX = "auth:reset:"


@dataclass
class TokenPair:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int | None = None


class AuthService:
    """High-level auth helpers dealing with JWTs and Redis state."""

    @staticmethod
    def issue_token_pair(
        *,
        user: User,
        tenant: Tenant,
        settings: Settings,
        redis: Redis,
    ) -> TokenPair:
        roles: list[str] = []
        for user_role in user.roles:
            role_obj = getattr(user_role, "role", None)
            if role_obj is not None:
                roles.append(role_obj.key.value)
        tenant_claims = {
            "tenant_id": str(tenant.id),
            "tenant_slug": tenant.slug,
            "roles": roles,
        }

        access_token = create_access_token(
            subject=str(user.id),
            settings=settings,
            additional_claims={
                **tenant_claims,
                "token_type": "access",
                "jti": str(uuid.uuid4()),
            },
        )

        refresh_jti = str(uuid.uuid4())
        refresh_token = create_refresh_token(
            subject=str(user.id),
            settings=settings,
            additional_claims={
                **tenant_claims,
                "token_type": "refresh",
                "jti": refresh_jti,
            },
        )

        AuthService.store_refresh_token(
            redis=redis,
            jti=refresh_jti,
            user_id=user.id,
            ttl_minutes=settings.jwt_refresh_token_expires_minutes,
        )

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.jwt_access_token_expires_minutes * 60,
        )

    @staticmethod
    def store_refresh_token(*, redis: Redis, jti: str, user_id: uuid.UUID, ttl_minutes: int) -> None:
        redis.setex(f"{REFRESH_TOKEN_PREFIX}{jti}", timedelta(minutes=ttl_minutes), str(user_id))

    @staticmethod
    def revoke_refresh_token(*, redis: Redis, jti: str) -> None:
        redis.delete(f"{REFRESH_TOKEN_PREFIX}{jti}")

    @staticmethod
    def validate_refresh_token(
        *,
        token: str,
        settings: Settings,
        redis: Redis,
    ) -> dict[str, Any]:
        payload = decode_token(token, settings=settings, refresh=True)
        if payload.get("token_type") != "refresh":
            raise InvalidTokenError("Invalid refresh token")
        jti = payload.get("jti")
        if not jti:
            raise InvalidTokenError("Malformed refresh token")
        if redis.get(f"{REFRESH_TOKEN_PREFIX}{jti}") is None:
            raise InvalidTokenError("Refresh token revoked")
        return payload

    @staticmethod
    def create_password_reset_token(
        *, redis: Redis, settings: Settings, tenant_id: uuid.UUID, user_id: uuid.UUID
    ) -> str:
        token = uuid.uuid4().hex
        ttl = settings.password_reset_token_expires_minutes
        redis.setex(
            f"{RESET_TOKEN_PREFIX}{token}",
            timedelta(minutes=ttl),
            f"{tenant_id}:{user_id}",
        )
        return token

    @staticmethod
    def consume_password_reset_token(*, redis: Redis, token: str) -> tuple[uuid.UUID, uuid.UUID] | None:
        value = redis.get(f"{RESET_TOKEN_PREFIX}{token}")
        if value is None:
            return None
        redis.delete(f"{RESET_TOKEN_PREFIX}{token}")
        tenant_str, user_str = value.split(":", 1)
        return uuid.UUID(tenant_str), uuid.UUID(user_str)


__all__ = ["AuthService", "TokenPair"]
