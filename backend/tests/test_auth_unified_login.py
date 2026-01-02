import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.admin import Admin
from backend.app.models.student import Student
from backend.app.models.professor import Professor
from backend.app.services.security import get_password_hash
from backend.app.services.jwt import decode_access_token


def _suffix() -> str:
    return uuid.uuid4().hex[:8]


def _create_admin(db: Session, password: str = "password123") -> Admin:
    s = _suffix()
    admin = Admin(
        username=f"admin_{s}",
        password_hash=get_password_hash(password),
        national_id=f"nid_{s}",
        email=f"admin_{s}@example.com",
        is_active=True,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


def _create_student(db: Session, password: str = "password123") -> Student:
    s = _suffix()
    student = Student(
        student_number=f"stu_{s}",
        full_name="Test Student",
        email=f"student_{s}@example.com",
        national_id=f"NID_{s}",
        phone_number=f"0912{s[:7]}",
        major="Computer Engineering",
        entry_year=2023,
        units_taken=0,
        mark=None,
        password_hash=get_password_hash(password),
        is_active=True,
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


def _create_professor(db: Session, password: str = "password123") -> Professor:
    s = _suffix()
    # Adjust fields if your Professor model has additional required columns.
    professor = Professor(
        professor_code=f"prof_{s}",
        full_name="Test Professor",
        email=f"prof_{s}@example.com",
        password_hash=get_password_hash(password),
        is_active=True,
    )
    db.add(professor)
    db.commit()
    db.refresh(professor)
    return professor


def _assert_login_success(resp, expected_role: str, expected_sub: str) -> None:
    assert resp.status_code == 200, resp.text
    data = resp.json()

    assert "access_token" in data
    assert "token_type" in data

    token = data["access_token"]
    payload = decode_access_token(token)
    assert payload.get("role") == expected_role
    assert payload.get("sub") == expected_sub

    # Optional: if your API returns user info alongside token
    if "user" in data:
        assert isinstance(data["user"], dict)
        assert data["user"].get("role") == expected_role


def test_admin_can_login_via_unified_auth_login(client: TestClient, db_session: Session) -> None:
    pw = "password123"
    admin = _create_admin(db_session, password=pw)

    resp = client.post("/auth/login", json={"username": admin.username, "password": pw})
    _assert_login_success(resp, expected_role="admin", expected_sub=admin.username)


def test_student_can_login_via_unified_auth_login(client: TestClient, db_session: Session) -> None:
    pw = "password123"
    student = _create_student(db_session, password=pw)

    resp = client.post("/auth/login", json={"username": student.student_number, "password": pw})
    _assert_login_success(resp, expected_role="student", expected_sub=student.student_number)


def test_professor_can_login_via_unified_auth_login(client: TestClient, db_session: Session) -> None:
    pw = "password123"
    professor = _create_professor(db_session, password=pw)

    resp = client.post("/auth/login", json={"username": professor.professor_code, "password": pw})
    _assert_login_success(resp, expected_role="professor", expected_sub=professor.professor_code)


@pytest.mark.parametrize(
    "username,password",
    [
        ("does_not_exist_123", "password123"),   # unknown username
        ("admin_nope", "wrongpass"),            # wrong pass
    ],
)
def test_unified_login_wrong_credentials_returns_401(client: TestClient, username: str, password: str) -> None:
    resp = client.post("/auth/login", json={"username": username, "password": password})
    assert resp.status_code == 401, resp.text
