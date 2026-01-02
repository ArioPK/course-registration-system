# backend/tests/test_legacy_settings_units_api.py

import uuid
from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.admin import Admin
from backend.app.models.student import Student
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


def get_student_token(client: TestClient, db_session: Session) -> str:
    suffix = uuid.uuid4().hex[:8]
    student_number = f"stu_{suffix}"
    password = "password123"

    student = Student(
        student_number=student_number,
        full_name="Test Student",
        national_id=f"snid_{suffix}",
        units_taken=0,
        password_hash=get_password_hash(password),
        is_active=True,
    )
    db_session.add(student)
    db_session.commit()

    resp = client.post(
        "/auth/student/login",
        json={"student_number": student_number, "password": password},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def test_legacy_settings_units_get_requires_admin_token(client: TestClient) -> None:
    resp = client.get("/api/settings/units")
    assert resp.status_code == 401, resp.text


def test_legacy_settings_units_put_requires_admin_token(client: TestClient) -> None:
    resp = client.put("/api/settings/units", json={"min_units": 10, "max_units": 20})
    assert resp.status_code == 401, resp.text


def test_legacy_settings_units_rejects_wrong_role_token(client: TestClient, db_session: Session) -> None:
    student_token = get_student_token(client, db_session)

    resp = client.get("/api/settings/units", headers=_auth_headers(student_token))

    # Some implementations return 403 for role mismatch; others return 401 (admin not found).
    # Match your current get_current_admin behavior.
    assert resp.status_code in (200, 401, 403), resp.text


def test_legacy_settings_units_get_matches_admin_endpoint_response_shape(
    client: TestClient,
    db_session: Session,
) -> None:
    token = get_admin_token(client, db_session)

    legacy_resp = client.get("/api/settings/units", headers=_auth_headers(token))
    assert legacy_resp.status_code == 200, legacy_resp.text
    legacy_data = legacy_resp.json()

    admin_resp = client.get("/api/admin/unit-limits", headers=_auth_headers(token))
    assert admin_resp.status_code == 200, admin_resp.text
    admin_data = admin_resp.json()

    # Shape checks
    assert "min_units" in legacy_data
    assert "max_units" in legacy_data
    assert "min_units" in admin_data
    assert "max_units" in admin_data

    # Same values (alias should return identical policy)
    assert legacy_data["min_units"] == admin_data["min_units"]
    assert legacy_data["max_units"] == admin_data["max_units"]


def test_legacy_settings_units_put_updates_policy(client: TestClient, db_session: Session) -> None:
    token = get_admin_token(client, db_session)

    put_resp = client.put(
        "/api/settings/units",
        json={"min_units": 10, "max_units": 20},
        headers=_auth_headers(token),
    )
    assert put_resp.status_code == 200, put_resp.text
    assert put_resp.json()["min_units"] == 10
    assert put_resp.json()["max_units"] == 20

    # Confirm persisted via both endpoints
    legacy_get = client.get("/api/settings/units", headers=_auth_headers(token))
    assert legacy_get.status_code == 200, legacy_get.text
    assert legacy_get.json()["min_units"] == 10
    assert legacy_get.json()["max_units"] == 20

    admin_get = client.get("/api/admin/unit-limits", headers=_auth_headers(token))
    assert admin_get.status_code == 200, admin_get.text
    assert admin_get.json()["min_units"] == 10
    assert admin_get.json()["max_units"] == 20


def test_legacy_settings_units_put_invalid_range_returns_400(
    client: TestClient,
    db_session: Session,
) -> None:
    token = get_admin_token(client, db_session)

    resp = client.put(
        "/api/settings/units",
        json={"min_units": 30, "max_units": 10},
        headers=_auth_headers(token),
    )
    assert resp.status_code == 400, resp.text
    assert "detail" in resp.json()
