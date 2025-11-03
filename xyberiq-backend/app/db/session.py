"""Database engine and session management."""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker, with_loader_criteria

from app.core.config import get_settings
from app.core.tenant import get_current_tenant_id
from app.db.base import TenantScopedMixin


class TenantSession(Session):
    """Custom session with tenant-aware filtering."""

    pass


def _create_engine() -> Engine:
    settings = get_settings()
    return create_engine(
        settings.database_url,
        echo=settings.database_echo,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        future=True,
    )


engine = _create_engine()

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, class_=TenantSession)


@event.listens_for(SessionLocal.class_, "do_orm_execute")
def _add_tenant_filter(execute_state) -> None:
    tenant_id = get_current_tenant_id()
    tenant_aware = execute_state.execution_options.get("tenant_aware", True)
    if not tenant_aware or tenant_id is None:
        return

    if execute_state.is_select:
        execute_state.statement = execute_state.statement.options(
            with_loader_criteria(
                TenantScopedMixin,
                lambda cls: cls.tenant_id == tenant_id,
                include_aliases=True,
            )
        )


@event.listens_for(SessionLocal.class_, "before_flush")
def _set_tenant_on_new_objects(session: Session, flush_context, instances) -> None:
    tenant_id = get_current_tenant_id()
    if tenant_id is None:
        return

    for obj in session.new:
        if isinstance(obj, TenantScopedMixin) and getattr(obj, "tenant_id", None) is None:
            obj.tenant_id = tenant_id


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """Provide a transactional scope for a series of operations."""

    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:  # pragma: no cover - re-raised
        session.rollback()
        raise
    finally:
        session.close()


__all__ = ["engine", "SessionLocal", "session_scope"]
