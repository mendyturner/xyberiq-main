"""User schemas."""

from __future__ import annotations

import uuid
from typing import List

from pydantic import EmailStr

from app.db.models import RoleKey, UserStatus
from app.schemas.base import APIModel


class RoleRead(APIModel):
    key: RoleKey
    name: str


class UserRead(APIModel):
    id: uuid.UUID
    email: EmailStr
    first_name: str
    last_name: str
    department: str | None = None
    title: str | None = None
    status: UserStatus
    roles: List[RoleKey]


__all__ = ["UserRead", "RoleRead"]
