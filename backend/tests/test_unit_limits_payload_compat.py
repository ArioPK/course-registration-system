# backend/tests/test_unit_limits_payload_compat.py

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
    s = uuid.uuid4().hex[:8]
    username = f"admin_{s}"
    password = "password123"

    admin = Admin(
        username=username,
        password_hash=get_password_hash(password),
        national_id=f"nid_{s}",
        email=f"{username}@example.com",
        is_active=True,
    )
    db_session.add(admin)
    db_session.commit()

    resp = client.post("/auth/login", json={"username": username, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def get_student_token(client: TestClient, db_session: Session) -> str:
    s = uuid.uuid4().hex[:8]
    student_number = f"stu_{s}"
    password = "password123"

    student = Student(
        student_number=student_number,
        full_name="Test Student",
        national_id=f"snid_{s}",
        units_taken=0,
        password_hash=get_password_hash(password),
        is_active=True,
    )
    db_session.add(student)
    db_session.commit()

    resp = client.post("/auth/student/login", json={"student_number": student_number, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def _ensure_policy_exists(client: TestClient, token: str) -> None:
    # Some implementations create default policy row on first GET.
    r = client.get("/api/admin/unit-limits", headers=_auth_headers(token))
    assert r.status_code == 200, r.text


# --- Auth tests (minimal) ---

def test_settings_units_put_requires_admin_token(client: TestClient) -> None:
    r = client.put("/api/settings/units", json={"min_units": 10, "max_units": 20})
    assert r.status_code == 401


def test_admin_unit_limits_put_requires_admin_token(client: TestClient) -> None:
    r = client.put("/api/admin/unit-limits", json={"min_units": 10, "max_units": 20})
    assert r.status_code == 401


def test_settings_units_put_rejects_wrong_role_token(client: TestClient, db_session: Session) -> None:
    token = get_student_token(client, db_session)
    r = client.put("/api/settings/units", json={"min_units": 10, "max_units": 20}, headers=_auth_headers(token))
    assert r.status_code in (401, 403)


# --- Alias endpoint payload compatibility ---

def test_settings_units_put_accepts_snake_case(client: TestClient, db_session: Session) -> None:
    token = get_admin_token(client, db_session)
    _ensure_policy_exists(client, token)

    r = client.put(
        "/api/settings/units",
        json={"min_units": 10, "max_units": 20},
        headers=_auth_headers(token),
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["min_units"] == 10
    assert data["max_units"] == 20


def test_settings_units_put_accepts_camel_case(client: TestClient, db_session: Session) -> None:
    token = get_admin_token(client, db_session)
    _ensure_policy_exists(client, token)

    r = client.put(
        "/api/settings/units",
        json={"minUnits": 11, "maxUnits": 21},
        headers=_auth_headers(token),
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["min_units"] == 11
    assert data["max_units"] == 21


def test_settings_units_put_missing_keys_returns_400(client: TestClient, db_session: Session) -> None:
    token = get_admin_token(client, db_session)
    _ensure_policy_exists(client, token)

    r = client.put(
        "/api/settings/units",
        json={"minUnits": 10},  # missing max
        headers=_auth_headers(token),
    )
    assert r.status_code == 400, r.text
    assert "Missing required keys" in r.json().get("detail", "")


def test_settings_units_put_invalid_range_returns_400(client: TestClient, db_session: Session) -> None:
    token = get_admin_token(client, db_session)
    _ensure_policy_exists(client, token)

    r = client.put(
        "/api/settings/units",
        json={"minUnits": 30, "maxUnits": 10},
        headers=_auth_headers(token),
    )
    assert r.status_code == 400, r.text


# --- Canonical endpoint payload compatibility (if you applied normalization there too) ---

def test_admin_unit_limits_put_accepts_camel_case(client: TestClient, db_session: Session) -> None:
    token = get_admin_token(client, db_session)
    _ensure_policy_exists(client, token)

    r = client.put(
        "/api/admin/unit-limits",
        json={"minUnits": 12, "maxUnits": 22},
        headers=_auth_headers(token),
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["min_units"] == 12
    assert data["max_units"] == 22
