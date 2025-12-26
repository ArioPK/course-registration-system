# backend/tests/test_auth_login.py

import uuid
import pytest

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from typing import Dict

from backend.app.models.admin import Admin
from backend.app.models.student import Student
from backend.app.models.professor import Professor
from backend.app.services.security import get_password_hash
from backend.app.services.jwt import decode_access_token


@pytest.fixture
def admin_credentials(db_session: Session) -> Dict[str, str]:
    username = f"admin_test_{uuid.uuid4().hex[:8]}"
    plain_password = "password123"
    national_id = uuid.uuid4().hex[:10]

    admin = Admin(
        username=username,
        national_id=national_id,
        email=f"{username}@example.com",
        password_hash=get_password_hash(plain_password),
        is_active=True,
    )
    db_session.add(admin)
    db_session.commit()

    return {"username": username, "password": plain_password}


@pytest.fixture
def student_credentials(db_session: Session) -> Dict[str, str]:
    student_number = f"st_{uuid.uuid4().hex[:10]}"
    plain_password = "password123"
    national_id = f"nid_{uuid.uuid4().hex[:12]}"

    student = Student(
        student_number=student_number,
        full_name="Test Student",
        email=f"{student_number}@example.com",
        national_id=national_id,
        password_hash=get_password_hash(plain_password),
        is_active=True,
        units_taken=0,
    )
    db_session.add(student)
    db_session.commit()

    return {"student_number": student_number, "password": plain_password}


@pytest.fixture
def professor_credentials(db_session: Session) -> Dict[str, str]:
    professor_code = f"pr_{uuid.uuid4().hex[:10]}"
    plain_password = "password123"

    professor = Professor(
        professor_code=professor_code,
        full_name="Test Professor",
        email=f"{professor_code}@example.com",
        password_hash=get_password_hash(plain_password),
        is_active=True,
    )
    db_session.add(professor)
    db_session.commit()

    return {"professor_code": professor_code, "password": plain_password}


def test_admin_login_returns_user_role(client, db_session: Session, admin_credentials: Dict[str, str]) -> None:
    resp = client.post(
        "/auth/login",
        json={
            "username": admin_credentials["username"],
            "password": admin_credentials["password"],
        },
    )
    assert resp.status_code == 200, resp.text

    data = resp.json()
    assert "access_token" in data and isinstance(data["access_token"], str) and data["access_token"]
    assert data.get("token_type") == "bearer"

    assert "user" in data and isinstance(data["user"], dict)
    assert data["user"]["role"] == "admin"
    assert data["user"]["identifier"] == admin_credentials["username"]


def test_student_login_returns_user_role(client, db_session: Session, student_credentials: Dict[str, str]) -> None:
    resp = client.post(
        "/auth/student/login",
        json={
            "student_number": student_credentials["student_number"],
            "password": student_credentials["password"],
        },
    )
    assert resp.status_code == 200, resp.text

    data = resp.json()
    assert "access_token" in data and isinstance(data["access_token"], str) and data["access_token"]
    assert data.get("token_type") == "bearer"

    assert "user" in data and isinstance(data["user"], dict)
    assert data["user"]["role"] == "student"
    assert data["user"]["identifier"] == student_credentials["student_number"]


def test_professor_login_returns_user_role(client, db_session: Session, professor_credentials: Dict[str, str]) -> None:
    resp = client.post(
        "/auth/professor/login",
        json={
            "professor_code": professor_credentials["professor_code"],
            "password": professor_credentials["password"],
        },
    )
    assert resp.status_code == 200, resp.text

    data = resp.json()
    assert "access_token" in data and isinstance(data["access_token"], str) and data["access_token"]
    assert data.get("token_type") == "bearer"

    assert "user" in data and isinstance(data["user"], dict)
    assert data["user"]["role"] == "professor"
    assert data["user"]["identifier"] == professor_credentials["professor_code"]


def test_admin_login_wrong_password(client, db_session: Session, admin_credentials: Dict[str, str]) -> None:
    response = client.post(
        "/auth/login",
        json={
            "username": admin_credentials["username"],
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401
    data = response.json()
    assert data.get("detail") == "Incorrect username or password"


def test_admin_login_unknown_username(client, db_session: Session) -> None:
    response = client.post(
        "/auth/login",
        json={
            "username": "no_such_user",
            "password": "whatever",
        },
    )

    assert response.status_code == 401
    data = response.json()
    assert data.get("detail") == "Incorrect username or password"


def test_admin_login_token_payload(client: TestClient, db_session: Session, admin_credentials: Dict[str, str]) -> None:
    response = client.post(
        "/auth/login",
        json={
            "username": admin_credentials["username"],
            "password": admin_credentials["password"],
        },
    )

    assert response.status_code == 200
    data = response.json()
    token = data["access_token"]

    payload = decode_access_token(token)
    assert payload.get("sub") == admin_credentials["username"]


def test_admin_login_token_contains_admin_role(client: TestClient, db_session: Session) -> None:
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

    token = resp.json()["access_token"]
    payload = decode_access_token(token)

    assert payload["sub"] == username
    assert payload["role"] == "admin"
