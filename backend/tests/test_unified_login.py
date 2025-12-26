# backend/tests/test_unified_login.py

import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.admin import Admin
from backend.app.models.student import Student
from backend.app.models.professor import Professor
from backend.app.services.security import get_password_hash
from backend.app.services.jwt import decode_access_token


def _sfx() -> str:
    return uuid.uuid4().hex[:8]


def test_unified_login_admin_success(client: TestClient, db_session: Session) -> None:
    s = _sfx()
    username = f"admin_u_{s}"
    password = "admin_pass_123"

    admin = Admin(
        username=username,
        national_id=f"nid_{s}",
        email=f"{username}@example.com",
        password_hash=get_password_hash(password),
        is_active=True,
    )
    db_session.add(admin)
    db_session.commit()

    resp = client.post("/auth/login", json={"username": username, "password": password})
    assert resp.status_code == 200, resp.text

    data = resp.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert data["user"]["role"] == "admin"
    assert data["user"]["identifier"] == username

    payload = decode_access_token(data["access_token"])
    assert payload["sub"] == username
    assert payload["role"] == "admin"


def test_unified_login_student_success(client: TestClient, db_session: Session) -> None:
    s = _sfx()
    student_number = f"stu_u_{s}"
    password = "student_pass_123"

    student = Student(
        student_number=student_number,
        full_name="Unified Student",
        email=f"{student_number}@example.com",
        national_id=f"SNID_{s}",
        phone_number="09120000000",
        major="Computer Engineering",
        entry_year=2023,
        units_taken=0,
        mark=None,
        password_hash=get_password_hash(password),
        is_active=True,
    )
    db_session.add(student)
    db_session.commit()

    resp = client.post("/auth/login", json={"username": student_number, "password": password})
    assert resp.status_code == 200, resp.text

    data = resp.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert data["user"]["role"] == "student"
    assert data["user"]["identifier"] == student_number

    payload = decode_access_token(data["access_token"])
    assert payload["sub"] == student_number
    assert payload["role"] == "student"


def test_unified_login_professor_success(client: TestClient, db_session: Session) -> None:
    s = _sfx()
    professor_code = f"prof_u_{s}"
    password = "prof_pass_123"

    prof = Professor(
        professor_code=professor_code,
        full_name="Unified Professor",
        email=f"{professor_code}@example.com",
        password_hash=get_password_hash(password),
        is_active=True,
    )
    db_session.add(prof)
    db_session.commit()

    resp = client.post("/auth/login", json={"username": professor_code, "password": password})
    assert resp.status_code == 200, resp.text

    data = resp.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert data["user"]["role"] == "professor"
    assert data["user"]["identifier"] == professor_code

    payload = decode_access_token(data["access_token"])
    assert payload["sub"] == professor_code
    assert payload["role"] == "professor"


def test_unified_login_wrong_password_returns_401(client: TestClient, db_session: Session) -> None:
    s = _sfx()
    username = f"admin_wp_{s}"
    password = "correct_pw"

    admin = Admin(
        username=username,
        national_id=f"nid_{s}",
        email=f"{username}@example.com",
        password_hash=get_password_hash(password),
        is_active=True,
    )
    db_session.add(admin)
    db_session.commit()

    resp = client.post("/auth/login", json={"username": username, "password": "wrong_pw"})
    assert resp.status_code == 401
    assert resp.json().get("detail") == "Incorrect username or password"


def test_unified_login_unknown_username_returns_401(client: TestClient) -> None:
    resp = client.post("/auth/login", json={"username": "no_such_user_123", "password": "whatever"})
    assert resp.status_code == 401
    assert resp.json().get("detail") == "Incorrect username or password"


def test_unified_login_collision_uses_admin_precedence(client: TestClient, db_session: Session) -> None:
    """
    Collision precedence test (required):
    - Create Admin.username == X
    - Create Student.student_number == X
    - Login with admin password returns admin role
    - Login with student password MUST fail, because we stop at Admin match first and do not fall through.
    """
    s = _sfx()
    collision = f"X_{s}"

    admin_pw = "admin_pw_123"
    student_pw = "student_pw_123"

    admin = Admin(
        username=collision,
        national_id=f"nid_{s}",
        email=f"{collision}@example.com",
        password_hash=get_password_hash(admin_pw),
        is_active=True,
    )
    student = Student(
        student_number=collision,
        full_name="Collision Student",
        email=f"{collision}_stu@example.com",
        national_id=f"SNID_{s}",
        phone_number="09120000000",
        major="Computer Engineering",
        entry_year=2023,
        units_taken=0,
        mark=None,
        password_hash=get_password_hash(student_pw),
        is_active=True,
    )
    db_session.add_all([admin, student])
    db_session.commit()

    # Admin password -> admin wins
    resp_admin = client.post("/auth/login", json={"username": collision, "password": admin_pw})
    assert resp_admin.status_code == 200, resp_admin.text
    assert resp_admin.json()["user"]["role"] == "admin"

    # Student password -> should NOT fall through; must be 401
    resp_student = client.post("/auth/login", json={"username": collision, "password": student_pw})
    assert resp_student.status_code == 401
    assert resp_student.json().get("detail") == "Incorrect username or password"
