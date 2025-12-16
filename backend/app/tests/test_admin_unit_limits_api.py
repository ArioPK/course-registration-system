# backend/tests/test_admin_unit_limits_api.py

import uuid
from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.admin import Admin
from backend.app.services.security import get_password_hash


def _auth_headers(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def get_admin_token(client: TestClient, db_session: Session) -> str:
    suffix = uuid.uuid4().hex[:8]
    username = f"admin_{suffix}"
    password = "password123"

    admin = Admin(
        username=username,
        password_hash=get_password_hash(password),
        national_id=f"nid_{suffix}",
        email=f"{username}@example.com",
        is_active=True,
    )
    db_session.add(admin)
    db_session.commit()

    resp = client.post("/auth/login", json={"username": username, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def test_unit_limits_requires_admin_auth(client: TestClient) -> None:
    resp = client.get("/api/admin/unit-limits")
    assert resp.status_code == 401, resp.text


def test_admin_can_get_unit_limits(client: TestClient, db_session: Session) -> None:
    token = get_admin_token(client, db_session)

    resp = client.get("/api/admin/unit-limits", headers=_auth_headers(token))
    assert resp.status_code == 200, resp.text

    data = resp.json()
    assert "min_units" in data
    assert "max_units" in data


def test_admin_can_update_unit_limits_success(client: TestClient, db_session: Session) -> None:
    token = get_admin_token(client, db_session)

    put_resp = client.put(
        "/api/admin/unit-limits",
        json={"min_units": 10, "max_units": 20},
        headers=_auth_headers(token),
    )
    assert put_resp.status_code == 200, put_resp.text
    assert put_resp.json()["min_units"] == 10
    assert put_resp.json()["max_units"] == 20

    # Ensure persisted
    get_resp = client.get("/api/admin/unit-limits", headers=_auth_headers(token))
    assert get_resp.status_code == 200, get_resp.text
    assert get_resp.json()["min_units"] == 10
    assert get_resp.json()["max_units"] == 20


def test_admin_update_unit_limits_invalid_range_returns_400(
    client: TestClient, db_session: Session
) -> None:
    token = get_admin_token(client, db_session)

    resp = client.put(
        "/api/admin/unit-limits",
        json={"min_units": 30, "max_units": 10},
        headers=_auth_headers(token),
    )
    assert resp.status_code == 400, resp.text
    assert "detail" in resp.json()
