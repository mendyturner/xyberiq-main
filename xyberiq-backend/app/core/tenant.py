"""Tenant context management helpers."""

from __future__ import annotations

import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Iterator

from contextvars import ContextVar, Token


_tenant_id_ctx: ContextVar[uuid.UUID | None] = ContextVar("tenant_id", default=None)
_tenant_slug_ctx: ContextVar[str | None] = ContextVar("tenant_slug", default=None)


@dataclass
class TenantContextToken:
    tenant_id_token: Token[uuid.UUID | None]
    tenant_slug_token: Token[str | None] | None = None


def set_current_tenant(tenant_id: uuid.UUID | None, tenant_slug: str | None = None) -> TenantContextToken:
    """Bind the current tenant to the context and return context tokens."""

    slug_token: Token[str | None] | None = None
    if tenant_slug is not None:
        slug_token = _tenant_slug_ctx.set(tenant_slug)
    id_token = _tenant_id_ctx.set(tenant_id)
    return TenantContextToken(tenant_id_token=id_token, tenant_slug_token=slug_token)


def reset_current_tenant(token: TenantContextToken) -> None:
    """Reset the tenant context to the provided token state."""

    if token.tenant_slug_token is not None:
        _tenant_slug_ctx.reset(token.tenant_slug_token)
    _tenant_id_ctx.reset(token.tenant_id_token)


def get_current_tenant_id() -> uuid.UUID | None:
    """Return the tenant id bound to the current context, if any."""

    return _tenant_id_ctx.get()


def get_current_tenant_slug() -> str | None:
    """Return the tenant slug bound to the current context, if any."""

    return _tenant_slug_ctx.get()


@contextmanager
def tenant_context(tenant_id: uuid.UUID | None, tenant_slug: str | None = None) -> Iterator[None]:
    """Context manager that temporarily binds the tenant id."""

    token = set_current_tenant(tenant_id, tenant_slug)
    try:
        yield
    finally:
        reset_current_tenant(token)


__all__ = [
    "set_current_tenant",
    "reset_current_tenant",
    "get_current_tenant_id",
    "get_current_tenant_slug",
    "tenant_context",
    "TenantContextToken",
]
