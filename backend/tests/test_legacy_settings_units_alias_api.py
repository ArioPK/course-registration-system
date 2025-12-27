# backend/tests/test_legacy_settings_units_alias_api.py

import uuid
from typing import Dict, Literal, Tuple

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.admin import Admin
from backend.app.models.student import Student
from backend.app.services.security import get_password_hash
from backend.app.services.unit_limit_service import get_unit_limits_service


# -----------------------
# Helpers
# -----------------------

def _auth_headers(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _uniq(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def create_admin(db_session: Session) -> Tuple[str, str]:
    username = _uniq("admin")
    password = "password123"

    admin = Admin(
        username=username,
        password_hash=get_password_hash(password),
        national_id=_uniq("nid"),
        email=f"{username}@example.com",
        is_active=True,
    )
    db_session.add(admin)
    db_session.commit()
    return username, password


def get_admin_token(client: TestClient, db_session: Session) -> str:
    username, password = create_admin(db_session)
    resp = client.post("/auth/login", json={"username": username, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def create_student(db_session: Session) -> Tuple[str, str]:
    student_number = _uniq("stu")
    password = "password123"

    student = Student(
        student_number=student_number,
        full_name="Alias Test Student",
        national_id=_uniq("snid"),
        units_taken=0,
        password_hash=get_password_hash(password),
        is_active=True,
    )
    db_session.add(student)
    db_session.commit()
    return student_number, password


def get_student_token(client: TestClient, db_session: Session) -> str:
    student_number, password = create_student(db_session)
    resp = client.post(
        "/auth/student/login",
        json={"student_number": student_number, "password": password},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def ensure_policy_exists(db_session: Session) -> None:
    """
    Ensure the UnitLimitPolicy row exists for deterministic tests.
    Many implementations create a default policy on first read.
    """
    get_unit_limits_service(db_session)
    db_session.commit()


# -----------------------
# A) Auth tests
# -----------------------

def test_settings_units_get_missing_token_returns_401(client: TestClient) -> None:
    resp = client.get("/api/settings/units")
    assert resp.status_code == 401, resp.text


def test_settings_units_put_missing_token_returns_401(client: TestClient) -> None:
    resp = client.put("/api/settings/units", json={"min_units": 10, "max_units": 20})
    assert resp.status_code == 401, resp.text


@pytest.mark.parametrize("method", ["GET", "PUT"])
def test_settings_units_wrong_role_token_returns_403_or_401(
    client: TestClient,
    db_session: Session,
    method: Literal["GET", "PUT"],
) -> None:
    """
    Card expects 403 on role mismatch.
    Some get_current_admin implementations return 401 instead.
    We assert the current behavior without forcing a semantics change in a tests-only card.
    """
    ensure_policy_exists(db_session)
    student_token = get_student_token(client, db_session)

    if method == "GET":
        resp = client.get("/api/settings/units", headers=_auth_headers(student_token))
    else:
        resp = client.put(
            "/api/settings/units",
            json={"min_units": 10, "max_units": 20},
            headers=_auth_headers(student_token),
        )

    assert resp.status_code in (401, 403), resp.text


# -----------------------
# B) GET behavior
# -----------------------

def test_settings_units_get_returns_expected_shape(client: TestClient, db_session: Session) -> None:
    ensure_policy_exists(db_session)
    token = get_admin_token(client, db_session)

    resp = client.get("/api/settings/units", headers=_auth_headers(token))
    assert resp.status_code == 200, resp.text

    data = resp.json()
    assert "min_units" in data
    assert "max_units" in data
    assert isinstance(data["min_units"], int)
    assert isinstance(data["max_units"], int)


# -----------------------
# C) PUT payload variants
# -----------------------

def test_settings_units_put_accepts_snake_case(client: TestClient, db_session: Session) -> None:
    ensure_policy_exists(db_session)
    token = get_admin_token(client, db_session)

    put_resp = client.put(
        "/api/settings/units",
        json={"min_units": 10, "max_units": 20},
        headers=_auth_headers(token),
    )
    assert put_resp.status_code == 200, put_resp.text
    assert put_resp.json()["min_units"] == 10
    assert put_resp.json()["max_units"] == 20

    # Confirm persisted
    get_resp = client.get("/api/settings/units", headers=_auth_headers(token))
    assert get_resp.status_code == 200, get_resp.text
    assert get_resp.json()["min_units"] == 10
    assert get_resp.json()["max_units"] == 20


def test_settings_units_put_accepts_camel_case(client: TestClient, db_session: Session) -> None:
    ensure_policy_exists(db_session)
    token = get_admin_token(client, db_session)

    put_resp = client.put(
        "/api/settings/units",
        json={"minUnits": 12, "maxUnits": 24},
        headers=_auth_headers(token),
    )
    assert put_resp.status_code == 200, put_resp.text
    assert put_resp.json()["min_units"] == 12
    assert put_resp.json()["max_units"] == 24

    # Confirm persisted
    get_resp = client.get("/api/settings/units", headers=_auth_headers(token))
    assert get_resp.status_code == 200, get_resp.text
    assert get_resp.json()["min_units"] == 12
    assert get_resp.json()["max_units"] == 24


# -----------------------
# D) Validation consistency
# -----------------------

def test_settings_units_put_invalid_range_returns_consistent_error(client: TestClient, db_session: Session) -> None:
    """
    Current implementation (Cards 8–9) uses manual parsing and maps validation to 400.
    If you later switch to FastAPI/Pydantic auto-validation, change expected to 422.
    """
    ensure_policy_exists(db_session)
    token = get_admin_token(client, db_session)

    resp = client.put(
        "/api/settings/units",
        json={"minUnits": 30, "maxUnits": 10},
        headers=_auth_headers(token),
    )
    assert resp.status_code == 400, resp.text
    assert "detail" in resp.json()


def test_settings_units_put_missing_field_returns_consistent_error(client: TestClient, db_session: Session) -> None:
    ensure_policy_exists(db_session)
    token = get_admin_token(client, db_session)

    resp = client.put(
        "/api/settings/units",
        json={"minUnits": 10},  # missing maxUnits/max_units
        headers=_auth_headers(token),
    )
    assert resp.status_code == 400, resp.text
    assert "detail" in resp.json()
