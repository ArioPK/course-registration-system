# backend/tests/test_unified_login.py

"""
Regression tests for unified login shim (Card 2):

POST /auth/login accepts {username, password} and authenticates by precedence:
  1) Admin.username
  2) Student.student_number
  3) Professor.professor_code

These tests verify:
- success for all 3 roles via /auth/login only
- generic 401 responses for wrong creds (no user enumeration)
- optional: JWT role/sub claims
- optional: collision precedence (Admin wins)
"""

import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.admin import Admin
from backend.app.models.student import Student
from backend.app.models.professor import Professor
from backend.app.services.security import get_password_hash
from backend.app.services.jwt import decode_access_token


def _uniq(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def _assert_success_response(data: dict) -> None:
    assert "access_token" in data and isinstance(data["access_token"], str) and data["access_token"]
    assert data.get("token_type") == "bearer"
    assert "user" in data and isinstance(data["user"], dict)
    assert "role" in data["user"]
    assert "identifier" in data["user"]


def _assert_generic_401(resp) -> None:
    assert resp.status_code == 401
    body = resp.json()
    detail = (body.get("detail") or "").lower()

    # Prefer stable exact message if your backend uses it.
    # Keep it flexible enough to not break on minor phrasing changes.
    assert "incorrect" in detail

    # Ensure no user enumeration / role leakage
    assert "student" not in detail
    assert "professor" not in detail
    assert "admin" not in detail


def test_unified_login_admin_success_returns_role(client: TestClient, db_session: Session) -> None:
    username = _uniq("admin_user")
    password = "AdminPass123!"

    admin = Admin(
        username=username,
        national_id=_uniq("nid"),
        email=f"{username}@example.com",
        password_hash=get_password_hash(password),
        is_active=True,
    )
    db_session.add(admin)
    db_session.commit()

    resp = client.post("/auth/login", json={"username": username, "password": password})
    assert resp.status_code == 200, resp.text

    data = resp.json()
    _assert_success_response(data)

    assert data["user"]["role"] == "admin"
    assert data["user"]["identifier"] == username


def test_unified_login_student_success_returns_role(client: TestClient, db_session: Session) -> None:
    student_number = _uniq("stu")
    password = "StudentPass123!"

    student = Student(
        student_number=student_number,
        full_name="Test Student",
        national_id=_uniq("snid"),
        password_hash=get_password_hash(password),
        is_active=True,
        units_taken=0,
    )
    db_session.add(student)
    db_session.commit()

    resp = client.post("/auth/login", json={"username": student_number, "password": password})
    assert resp.status_code == 200, resp.text

    data = resp.json()
    _assert_success_response(data)

    assert data["user"]["role"] == "student"
    assert data["user"]["identifier"] == student_number


def test_unified_login_professor_success_returns_role(client: TestClient, db_session: Session) -> None:
    professor_code = _uniq("prof")
    password = "ProfessorPass123!"

    professor = Professor(
        professor_code=professor_code,
        full_name="Test Professor",
        password_hash=get_password_hash(password),
        is_active=True,
    )
    db_session.add(professor)
    db_session.commit()

    resp = client.post("/auth/login", json={"username": professor_code, "password": password})
    assert resp.status_code == 200, resp.text

    data = resp.json()
    _assert_success_response(data)

    assert data["user"]["role"] == "professor"
    assert data["user"]["identifier"] == professor_code


def test_unified_login_wrong_password_returns_401(client: TestClient, db_session: Session) -> None:
    username = _uniq("admin_wrongpw")
    correct_password = "CorrectPass123!"

    admin = Admin(
        username=username,
        national_id=_uniq("nid"),
        email=f"{username}@example.com",
        password_hash=get_password_hash(correct_password),
        is_active=True,
    )
    db_session.add(admin)
    db_session.commit()

    resp = client.post("/auth/login", json={"username": username, "password": "WrongPass!!!"})
    _assert_generic_401(resp)


def test_unified_login_unknown_username_returns_401(client: TestClient) -> None:
    resp = client.post("/auth/login", json={"username": "no_such_user_12345", "password": "anything"})
    _assert_generic_401(resp)


def test_unified_login_token_contains_role_claim(client: TestClient, db_session: Session) -> None:
    """
    Optional (stable): verify JWT payload contains role + sub matching identifier.
    """
    student_number = _uniq("stu_claim")
    password = "StudentPass123!"

    student = Student(
        student_number=student_number,
        full_name="Claim Student",
        national_id=_uniq("snid"),
        password_hash=get_password_hash(password),
        is_active=True,
        units_taken=0,
    )
    db_session.add(student)
    db_session.commit()

    resp = client.post("/auth/login", json={"username": student_number, "password": password})
    assert resp.status_code == 200, resp.text

    token = resp.json()["access_token"]
    payload = decode_access_token(token)

    assert payload.get("sub") == student_number
    assert payload.get("role") == "student"


def test_unified_login_collision_admin_precedence(client: TestClient, db_session: Session) -> None:
    """
    Collision precedence (required/valuable):
    - Admin.username == X
    - Student.student_number == X
    Precedence is Admin -> Student -> Professor.

    Behavior:
    - Login with admin password => success as admin
    - Login with student password => FAILS with 401 (we do not fall through after admin match)
    """
    collision_id = _uniq("collision")

    admin_pw = "AdminPass123!"
    student_pw = "StudentPass123!"

    admin = Admin(
        username=collision_id,
        national_id=_uniq("nid"),
        email=f"{collision_id}@example.com",
        password_hash=get_password_hash(admin_pw),
        is_active=True,
    )

    student = Student(
        student_number=collision_id,
        full_name="Collision Student",
        national_id=_uniq("snid"),
        password_hash=get_password_hash(student_pw),
        is_active=True,
        units_taken=0,
    )

    db_session.add_all([admin, student])
    db_session.commit()

    # Admin password -> admin wins
    resp_admin = client.post("/auth/login", json={"username": collision_id, "password": admin_pw})
    assert resp_admin.status_code == 200, resp_admin.text
    data_admin = resp_admin.json()
    _assert_success_response(data_admin)
    assert data_admin["user"]["role"] == "admin"
    assert data_admin["user"]["identifier"] == collision_id

    # Student password -> should NOT fall through; must return generic 401
    resp_student = client.post("/auth/login", json={"username": collision_id, "password": student_pw})
    _assert_generic_401(resp_student)
