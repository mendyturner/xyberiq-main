"""Authentication endpoint tests."""

from __future__ import annotations

from fastapi.testclient import TestClient


def register_default_tenant(client: TestClient) -> dict[str, str]:
    payload = {
        "name": "Acme Healthcare",
        "slug": "acme-health",
        "contact_email": "admin@acmehealth.com",
        "admin": {
            "email": "admin@acmehealth.com",
            "password": "SuperSecure123!",
            "first_name": "Alice",
            "last_name": "Admin",
        },
    }
    response = client.post("/auth/register-tenant", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def test_register_and_me_flow(client: TestClient) -> None:
    tokens = register_default_tenant(client)

    headers = {
        "Authorization": f"Bearer {tokens['access_token']}",
        "X-Tenant": "acme-health",
    }
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "admin@acmehealth.com"
    assert "admin" in data["roles"]


def test_login_requires_correct_tenant(client: TestClient) -> None:
    register_default_tenant(client)

    login_payload = {"email": "admin@acmehealth.com", "password": "SuperSecure123!"}

    ok = client.post("/auth/login", json=login_payload, headers={"X-Tenant": "acme-health"})
    assert ok.status_code == 200

    bad = client.post("/auth/login", json=login_payload, headers={"X-Tenant": "other-tenant"})
    assert bad.status_code in {401, 404}


def test_refresh_rotates_token(client: TestClient) -> None:
    tokens = register_default_tenant(client)
    refresh_token = tokens["refresh_token"]

    response = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    new_tokens = response.json()
    assert new_tokens["refresh_token"] != refresh_token

    second = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert second.status_code == 401


def test_logout_revokes_refresh_token(client: TestClient) -> None:
    tokens = register_default_tenant(client)
    refresh_token = tokens["refresh_token"]

    headers = {"X-Tenant": "acme-health"}
    response = client.post("/auth/logout", json={"refresh_token": refresh_token}, headers=headers)
    assert response.status_code == 204

    reused = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert reused.status_code == 401


def test_tenant_scoping_is_enforced(client: TestClient) -> None:
    register_default_tenant(client)

    second_payload = {
        "name": "Beta Security",
        "slug": "beta-sec",
        "contact_email": "owner@betasec.com",
        "admin": {
            "email": "owner@betasec.com",
            "password": "AnotherPass123!",
            "first_name": "Bob",
            "last_name": "Boss",
        },
    }
    response = client.post("/auth/register-tenant", json=second_payload)
    assert response.status_code == 201

    login_payload = {"email": "admin@acmehealth.com", "password": "SuperSecure123!"}
    wrong_tenant = client.post("/auth/login", json=login_payload, headers={"X-Tenant": "beta-sec"})
    assert wrong_tenant.status_code == 401
