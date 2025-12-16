# backend/tests/test_student_dependency.py

import uuid
from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.admin import Admin
from backend.app.models.student import Student
from backend.app.services.security import get_password_hash


def _auth_headers(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _unique_suffix() -> str:
    return uuid.uuid4().hex[:8]


def create_student_and_get_token(client: TestClient, db_session: Session) -> Dict[str, str]:
    suffix = _unique_suffix()
    student_number = f"stu_{suffix}"
    plain_password = "password123"

    student = Student(
        student_number=student_number,
        full_name="Test Student",
        email=f"student_{suffix}@example.com",
        national_id=f"NID_{suffix}",
        phone_number=f"0912{suffix[:7]}",
        major="Computer Engineering",
        entry_year=2023,
        units_taken=0,
        mark=None,
        password_hash=get_password_hash(plain_password),
        is_active=True,
    )
    db_session.add(student)
    db_session.commit()

    resp = client.post(
        "/auth/student/login",
        json={"student_number": student_number, "password": plain_password},
    )
    assert resp.status_code == 200, resp.text
    return {"student_number": student_number, "token": resp.json()["access_token"]}


def create_admin_and_get_token(client: TestClient, db_session: Session) -> str:
    suffix = _unique_suffix()
    username = f"admin_{suffix}"
    plain_password = "password123"

    admin = Admin(
        username=username,
        password_hash=get_password_hash(plain_password),
        national_id=f"nid_{suffix}",
        email=f"{username}@example.com",
        is_active=True,
    )
    db_session.add(admin)
    db_session.commit()

    resp = client.post("/auth/login", json={"username": username, "password": plain_password})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def test_get_current_student_rejects_invalid_token(client: TestClient) -> None:
    resp = client.get("/auth/student/me", headers={"Authorization": "Bearer invalidtoken"})
    assert resp.status_code == 401
    assert "detail" in resp.json()


def test_get_current_student_rejects_role_mismatch(client: TestClient, db_session: Session) -> None:
    admin_token = create_admin_and_get_token(client, db_session)
    resp = client.get("/auth/student/me", headers=_auth_headers(admin_token))
    assert resp.status_code == 403
    assert "detail" in resp.json()


def test_get_current_student_success(client: TestClient, db_session: Session) -> None:
    data = create_student_and_get_token(client, db_session)
    resp = client.get("/auth/student/me", headers=_auth_headers(data["token"]))

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["student_number"] == data["student_number"]
    assert "full_name" in body
