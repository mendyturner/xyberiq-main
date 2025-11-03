"""Authentication schemas."""

from __future__ import annotations

from pydantic import EmailStr, Field

from app.schemas.base import APIModel
from app.schemas.user import UserRead


class LoginRequest(APIModel):
    email: EmailStr
    password: str


class TokenResponse(APIModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int | None = None


class RefreshRequest(APIModel):
    refresh_token: str


class ForgotPasswordRequest(APIModel):
    email: EmailStr


class ResetPasswordRequest(APIModel):
    token: str
    new_password: str = Field(min_length=8)


class MeResponse(UserRead):
    pass


__all__ = [
    "LoginRequest",
    "TokenResponse",
    "RefreshRequest",
    "ForgotPasswordRequest",
    "ResetPasswordRequest",
    "MeResponse",
]
