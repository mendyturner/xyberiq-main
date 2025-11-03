"""Authentication and security helpers."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import JWTError, jwt

from app.core.config import Settings


password_hasher = PasswordHasher()


class InvalidTokenError(Exception):
    """Raised when a JWT token cannot be decoded."""


def create_access_token(
    subject: str,
    settings: Settings,
    expires_delta: timedelta | None = None,
    additional_claims: dict[str, Any] | None = None,
) -> str:
    """Generate a signed JWT access token."""

    expire = datetime.now(timezone.utc) + (
        expires_delta
        if expires_delta is not None
        else timedelta(minutes=settings.jwt_access_token_expires_minutes)
    )
    to_encode = {
        "sub": subject,
        "exp": expire,
        **(additional_claims or {}),
    }
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(
    subject: str,
    settings: Settings,
    expires_delta: timedelta | None = None,
    additional_claims: dict[str, Any] | None = None,
) -> str:
    """Generate a signed JWT refresh token."""

    expire = datetime.now(timezone.utc) + (
        expires_delta
        if expires_delta is not None
        else timedelta(minutes=settings.jwt_refresh_token_expires_minutes)
    )
    to_encode = {
        "sub": subject,
        "exp": expire,
        **(additional_claims or {}),
    }
    return jwt.encode(
        to_encode, settings.jwt_refresh_secret_key, algorithm=settings.jwt_algorithm
    )


def decode_token(token: str, *, settings: Settings, refresh: bool = False) -> dict[str, Any]:
    """Decode a JWT token and return its payload."""

    key = settings.jwt_refresh_secret_key if refresh else settings.jwt_secret_key
    try:
        return jwt.decode(token, key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:  # pragma: no cover - jose handles message variability
        raise InvalidTokenError("Invalid or expired token") from exc


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password hash produced by Argon2."""

    try:
        password_hasher.verify(hashed_password, plain_password)
        return True
    except VerifyMismatchError:
        return False


def get_password_hash(password: str) -> str:
    """Hash a password using Argon2."""

    return password_hasher.hash(password)


__all__ = [
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "verify_password",
    "get_password_hash",
    "InvalidTokenError",
]
