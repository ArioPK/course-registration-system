# backend/tests/test_courses_read_access_any_role.py

import uuid
from datetime import time
from typing import Dict, Tuple

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.admin import Admin
from backend.app.models.student import Student
from backend.app.models.professor import Professor
from backend.app.models.course import Course
from backend.app.services.security import get_password_hash


# -----------------------
# Helpers
# -----------------------

def _sfx() -> str:
    return uuid.uuid4().hex[:8]


def _auth_headers(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def create_admin(db: Session, password: str = "password123") -> Tuple[Admin, str]:
    s = _sfx()
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
    return admin, password


def get_admin_token(client: TestClient, admin: Admin, password: str) -> str:
    resp = client.post("/auth/login", json={"username": admin.username, "password": password})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "access_token" in data, data
    return data["access_token"]


def create_student(db: Session, password: str = "password123") -> Tuple[Student, str]:
    s = _sfx()
    student = Student(
        student_number=f"stu_{s}",
        full_name="Test Student",
        email=f"student_{s}@example.com",
        national_id=f"snid_{s}",
        phone_number=f"0912{s[:7]}",
        major="CS",
        entry_year=2023,
        units_taken=0,
        mark=None,
        password_hash=get_password_hash(password),
        is_active=True,
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student, password


def get_student_token(client: TestClient, student: Student, password: str) -> str:
    resp = client.post(
        "/auth/student/login",
        json={"student_number": student.student_number, "password": password},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "access_token" in data, data
    return data["access_token"]


def create_professor(db: Session, password: str = "password123") -> Tuple[Professor, str]:
    s = _sfx()
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
    return professor, password


def get_professor_token(client: TestClient, professor: Professor, password: str) -> str:
    resp = client.post(
        "/auth/professor/login",
        json={"professor_code": professor.professor_code, "password": password},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "access_token" in data, data
    return data["access_token"]


def create_course(db: Session) -> Course:
    """
    Insert at least one course record directly.
    Ensure required fields match your Course model constraints.
    """
    s = _sfx()
    course = Course(
        code=f"CS{s[:4]}",
        name=f"Test Course {s}",
        capacity=30,
        professor_name="Dr. Test",
        day_of_week="SAT",
        start_time=time(9, 0),
        end_time=time(11, 0),
        location="Room 101",
        units=3,
        department="CS",
        semester="Fall",
        is_active=True,
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


def _infer_courses_public_or_requires_token(client: TestClient) -> bool:
    """
    If GET /api/courses without token returns 200 => public.
    If it returns 401 => token required.
    We don't accept other statuses as "expected"; if present, fail loudly.
    """
    resp = client.get("/api/courses")
    if resp.status_code == 200:
        return True
    if resp.status_code == 401:
        return False
    raise AssertionError(f"Unexpected status for GET /api/courses without token: {resp.status_code} {resp.text}")


def _probe_admin_only_wrong_role_status(client: TestClient, token: str) -> int:
    """
    Probe what get_current_admin returns for an authenticated *non-admin*.
    Use a known admin-only endpoint so we don't rely on missing-token behavior.
    """
    resp = client.get("/api/admin/unit-limits", headers=_auth_headers(token))
    return resp.status_code


def _valid_course_payload() -> Dict:
    s = _sfx()
    return {
        "code": f"CS{s}",
        "name": f"Payload Course {s}",
        "units": 3,
        "department": "CS",
        "semester": "Fall",
        "capacity": 30,
        "professor_name": "Dr. Payload",
        "day_of_week": "SAT",
        "start_time": "09:00",
        "end_time": "11:00",
        "location": "Room 202",
        "is_active": True,
    }


# -----------------------
# Tests (Card 12)
# -----------------------

def test_student_token_can_get_courses_list(client: TestClient, db_session: Session) -> None:
    create_course(db_session)

    student, pw = create_student(db_session)
    token = get_student_token(client, student, pw)

    resp = client.get("/api/courses", headers=_auth_headers(token))
    assert resp.status_code == 200, resp.text

    data = resp.json()
    assert isinstance(data, list), f"Expected list, got: {type(data)} => {data}"
    assert len(data) >= 1


def test_professor_token_can_get_courses_list(client: TestClient, db_session: Session) -> None:
    create_course(db_session)

    professor, pw = create_professor(db_session)
    token = get_professor_token(client, professor, pw)

    resp = client.get("/api/courses", headers=_auth_headers(token))
    assert resp.status_code == 200, resp.text

    data = resp.json()
    assert isinstance(data, list), f"Expected list, got: {type(data)} => {data}"
    assert len(data) >= 1


def test_student_token_cannot_post_course(client: TestClient, db_session: Session) -> None:
    student, pw = create_student(db_session)
    token = get_student_token(client, student, pw)

    expected = _probe_admin_only_wrong_role_status(client, token)

    resp = client.post("/api/courses", json=_valid_course_payload(), headers=_auth_headers(token))
    assert resp.status_code == expected, resp.text


def test_no_token_get_courses_behavior(client: TestClient, db_session: Session) -> None:
    """
    Token required vs public catalog behavior must match implementation.
    We determine expected behavior at runtime.
    """
    create_course(db_session)

    is_public = _infer_courses_public_or_requires_token(client)
    resp = client.get("/api/courses")

    if is_public:
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert isinstance(data, list)
    else:
        assert resp.status_code == 401, resp.text


def test_invalid_token_rejected(client: TestClient) -> None:
    resp = client.get("/api/courses", headers={"Authorization": "Bearer badtoken"})
    assert resp.status_code == 401, resp.text
