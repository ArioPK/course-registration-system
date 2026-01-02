import uuid
from typing import Dict

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.admin import Admin
from backend.app.models.student import Student
from backend.app.models.professor import Professor
from backend.app.services.security import get_password_hash


def _auth_headers(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _unique() -> str:
    return uuid.uuid4().hex[:8]


def create_admin(db_session: Session, password: str = "password123") -> Admin:
    suffix = _unique()
    admin = Admin(
        username=f"admin_{suffix}",
        password_hash=get_password_hash(password),
        national_id=f"nid_{suffix}",
        email=f"admin_{suffix}@example.com",
        is_active=True,
    )
    db_session.add(admin)
    db_session.commit()
    return admin


def create_student(db_session: Session, password: str = "password123") -> Student:
    suffix = _unique()
    student = Student(
        student_number=f"stu_{suffix}",
        full_name="Test Student",
        email=f"student_{suffix}@example.com",
        national_id=f"NID_{suffix}",
        phone_number=f"0912{suffix[:7]}",
        major="Computer Engineering",
        entry_year=2023,
        units_taken=0,
        mark=None,
        password_hash=get_password_hash(password),
        is_active=True,
    )
    db_session.add(student)
    db_session.commit()
    return student


def create_professor(db_session: Session, password: str = "password123") -> Professor:
    suffix = _unique()
    professor = Professor(
        professor_code=f"prof_{suffix}",
        full_name="Test Professor",
        email=f"prof_{suffix}@example.com",
        password_hash=get_password_hash(password),
        is_active=True,
    )
    db_session.add(professor)
    db_session.commit()
    return professor


def login_unified(client: TestClient, username: str, password: str) -> str:
    resp = client.post("/auth/login", json={"username": username, "password": password})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert "access_token" in body
    return body["access_token"]


def create_course_via_admin_api(client: TestClient, admin_token: str) -> Dict:
    suffix = _unique()
    payload = {
        "code": f"CS{suffix}",
        "name": f"Course {suffix}",
        "units": 3,
        "department": "CS",
        "semester": "Fall",
        "capacity": 30,
        "professor_name": "Dr. X",
        "day_of_week": "SAT",
        "start_time": "09:00",
        "end_time": "11:00",
        "location": "Room 1",
        "is_active": True,
    }
    resp = client.post("/api/courses", json=payload, headers=_auth_headers(admin_token))
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_courses_get_missing_token_returns_401(client: TestClient):
    resp = client.get("/api/courses")
    assert resp.status_code == 401, resp.text


def test_courses_get_invalid_token_returns_401(client: TestClient):
    resp = client.get("/api/courses", headers={"Authorization": "Bearer badtoken"})
    assert resp.status_code == 401, resp.text


def test_student_token_can_get_courses_list_and_detail(
    client: TestClient, db_session: Session
):
    admin = create_admin(db_session)
    admin_token = login_unified(client, admin.username, "password123")
    created = create_course_via_admin_api(client, admin_token)
    course_id = created["id"]

    student = create_student(db_session)
    student_token = login_unified(client, student.student_number, "password123")

    list_resp = client.get("/api/courses", headers=_auth_headers(student_token))
    assert list_resp.status_code == 200, list_resp.text
    courses = list_resp.json()
    assert any(c["id"] == course_id for c in courses)

    detail_resp = client.get(f"/api/courses/{course_id}", headers=_auth_headers(student_token))
    assert detail_resp.status_code == 200, detail_resp.text
    assert detail_resp.json()["id"] == course_id


def test_professor_token_can_get_courses_list_and_detail(
    client: TestClient, db_session: Session
):
    admin = create_admin(db_session)
    admin_token = login_unified(client, admin.username, "password123")
    created = create_course_via_admin_api(client, admin_token)
    course_id = created["id"]

    prof = create_professor(db_session)
    prof_token = login_unified(client, prof.professor_code, "password123")

    list_resp = client.get("/api/courses", headers=_auth_headers(prof_token))
    assert list_resp.status_code == 200, list_resp.text
    courses = list_resp.json()
    assert any(c["id"] == course_id for c in courses)

    detail_resp = client.get(f"/api/courses/{course_id}", headers=_auth_headers(prof_token))
    assert detail_resp.status_code == 200, detail_resp.text
    assert detail_resp.json()["id"] == course_id


def test_student_cannot_create_course_still_admin_only(
    client: TestClient, db_session: Session
):
    student = create_student(db_session)
    token = login_unified(client, student.student_number, "password123")

    payload = {
        "code": f"CS{_unique()}",
        "name": "Should Fail",
        "units": 3,
        "department": "CS",
        "semester": "Fall",
        "capacity": 10,
        "professor_name": "Dr. Fail",
        "day_of_week": "SAT",
        "start_time": "09:00",
        "end_time": "10:00",
        "location": "Room X",
        "is_active": True,
    }

    resp = client.post("/api/courses", json=payload, headers=_auth_headers(token))
    assert resp.status_code in (401, 403), resp.text
