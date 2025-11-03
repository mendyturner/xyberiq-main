"""Tenant schemas."""

from __future__ import annotations

from pydantic import EmailStr, Field

from app.schemas.base import APIModel


class TenantBootstrapAdmin(APIModel):
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str
    last_name: str


class RegisterTenantRequest(APIModel):
    tenant_name: str = Field(..., alias="name")
    tenant_slug: str = Field(..., alias="slug")
    contact_email: EmailStr
    admin: TenantBootstrapAdmin


class TenantResponse(APIModel):
    id: str
    name: str
    slug: str
    contact_email: EmailStr


__all__ = [
    "TenantBootstrapAdmin",
    "RegisterTenantRequest",
    "TenantResponse",
]
