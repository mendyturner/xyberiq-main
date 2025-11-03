"""Basic health endpoint tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint_returns_ok() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"


def test_version_endpoint_returns_version_string() -> None:
    response = client.get("/version")
    assert response.status_code == 200
    payload = response.json()
    assert "version" in payload
