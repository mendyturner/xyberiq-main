"""Test configuration and fixtures."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID

from app.api.dependencies import get_db
from app.api.routes.auth import _redis_client
from app.db.base import Base
from app.db.session import TenantSession
from app.main import app

import fakeredis


@compiles(JSONB, "sqlite")
def _compile_jsonb(element, compiler, **kw):
    return "JSON"


@compiles(PGUUID, "sqlite")
def _compile_uuid(element, compiler, **kw):
    return "CHAR(36)"


engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    future=True,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(bind=engine, expire_on_commit=False, class_=TenantSession)


@pytest.fixture(scope="session", autouse=True)
def create_database() -> None:
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        if transaction.is_active:
            transaction.rollback()
        connection.close()


@pytest.fixture
def redis_client():
    client = fakeredis.FakeStrictRedis(decode_responses=True)
    try:
        yield client
    finally:
        client.flushall()


@pytest.fixture
def client(db_session, redis_client) -> TestClient:
    def override_get_db():
        try:
            yield db_session
        finally:
            if db_session.is_active:
                db_session.rollback()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[_redis_client] = lambda: redis_client

    test_client = TestClient(app)
    try:
        yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)
        app.dependency_overrides.pop(_redis_client, None)

