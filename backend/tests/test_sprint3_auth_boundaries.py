# backend/tests/test_sprint3_auth_boundaries.py

from datetime import time

import pytest

from backend.app.models.course import Course
from backend.app.models.professor import Professor
from backend.app.models.student import Student
from backend.app.services.jwt import create_access_token
from backend.tests.test_enrollment_service import _new_id

CURRENT_TERM = "1404-1"


def student_auth_headers(student: Student) -> dict:
    token = create_access_token(data={"sub": student.student_number, "role": "student"})
    return {"Authorization": f"Bearer {token}"}


def professor_auth_headers(professor: Professor) -> dict:
    # Keep consistent with get_current_professor lookup strategy used in your other tests 
    token = create_access_token(data={"sub": professor.professor_code, "role": "professor"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def student(db_session) -> Student:
    i = _new_id()
    s_num = f"S{i:05d}"
    s = Student(
        student_number=s_num,
        full_name=f"Student {i}",
        national_id=f"{i:010d}",
        email=f"{s_num}@test.local",
        phone_number="09120000000",
        major="CS",
        entry_year=1400,
        units_taken=0,
        password_hash="x",
        is_active=True,
    )
    db_session.add(s)
    db_session.commit()
    return s


@pytest.fixture
def professor(db_session) -> Professor:
    i = _new_id()
    p_num = f"P{i:05d}"
    p = Professor(
        professor_code=p_num,
        full_name="Dr. Alice Smith",
        # national_id=f"{i:010d}",
        email=f"{p_num}@test.local",
        # phone_number="09120000000",
        # department="CS",
        password_hash="x",
        is_active=True,
    )
    db_session.add(p)
    db_session.commit()
    return p


@pytest.fixture
def course(db_session, professor) -> Course:
    i = _new_id()
    c = Course(
        code=f"CS{i:03d}",
        name=f"Course {i}",
        capacity=30,
        professor_name=professor.full_name,
        day_of_week="MON",
        start_time=time(9, 0),
        end_time=time(10, 0),
        location="Room 101",
        is_active=True,
        units=3,
        department="CS",
        semester=CURRENT_TERM,
    )
    db_session.add(c)
    db_session.commit()
    return c


def _admin_course_payload(*, code: str) -> dict:
    # Provide a valid payload to avoid 422 masking auth failures.
    # Times as strings are typically accepted by Pydantic for time fields.
    return {
        "code": code,
        "name": f"Auth Boundary {code}",
        "capacity": 30,
        "professor_name": "Dr. Admin Owner",
        "day_of_week": "MON",
        "start_time": "09:00:00",
        "end_time": "10:00:00",
        "location": "Room 999",
        "is_active": True,
        "units": 3,
        "department": "CS",
        "semester": CURRENT_TERM,
    }


def test_no_token_protected_endpoints_return_401(client, monkeypatch, course, student):
    monkeypatch.setenv("CURRENT_TERM", CURRENT_TERM)

    # Student protected endpoints
    r = client.post("/api/student/enrollments", json={"courseId": course.id})
    assert r.status_code == 401, r.text

    r = client.delete(f"/api/student/enrollments/{course.id}")
    assert r.status_code == 401, r.text

    r = client.get("/api/student/schedule")
    assert r.status_code == 401, r.text

    # Professor protected endpoints
    r = client.get("/api/professor/courses")
    assert r.status_code == 401, r.text

    r = client.get(f"/api/professor/courses/{course.id}/students")
    assert r.status_code == 401, r.text

    r = client.delete(f"/api/professor/courses/{course.id}/students/{student.id}")
    assert r.status_code == 401, r.text


def test_student_cannot_access_professor_endpoints_403(client, monkeypatch, student, course):
    monkeypatch.setenv("CURRENT_TERM", CURRENT_TERM)
    headers = student_auth_headers(student)

    r = client.get("/api/professor/courses", headers=headers)
    assert r.status_code == 403, r.text

    r = client.get(f"/api/professor/courses/{course.id}/students", headers=headers)
    assert r.status_code == 403, r.text

    r = client.delete(f"/api/professor/courses/{course.id}/students/{student.id}", headers=headers)
    assert r.status_code == 403, r.text


def test_professor_cannot_access_student_endpoints_403(client, monkeypatch, professor, course):
    monkeypatch.setenv("CURRENT_TERM", CURRENT_TERM)
    headers = professor_auth_headers(professor)

    r = client.post("/api/student/enrollments", json={"courseId": course.id}, headers=headers)
    assert r.status_code == 403, r.text

    r = client.delete(f"/api/student/enrollments/{course.id}", headers=headers)
    assert r.status_code == 403, r.text

    r = client.get("/api/student/schedule", headers=headers)
    assert r.status_code == 403, r.text


def test_admin_only_course_mutations_remain_admin_only(client, monkeypatch, student, professor, course):
    monkeypatch.setenv("CURRENT_TERM", CURRENT_TERM)

    student_headers = student_auth_headers(student)
    professor_headers = professor_auth_headers(professor)

    # Use unique code per request to avoid accidental uniqueness conflicts if auth is broken.
    post_payload = _admin_course_payload(code=f"CS{_new_id():03d}")
    put_payload = _admin_course_payload(code=course.code)  # updating existing course; keep code stable

    # Student token -> 403
    r = client.post("/api/courses", json=post_payload, headers=student_headers)
    assert r.status_code == 403, r.text

    r = client.put(f"/api/courses/{course.id}", json=put_payload, headers=student_headers)
    assert r.status_code == 403, r.text

    r = client.delete(f"/api/courses/{course.id}", headers=student_headers)
    assert r.status_code == 403, r.text

    # Professor token -> 403
    r = client.post("/api/courses", json=post_payload, headers=professor_headers)
    assert r.status_code == 403, r.text

    r = client.put(f"/api/courses/{course.id}", json=put_payload, headers=professor_headers)
    assert r.status_code == 403, r.text

    r = client.delete(f"/api/courses/{course.id}", headers=professor_headers)
    assert r.status_code == 403, r.text

    # No token -> 401 (send valid payload to avoid 422 masking auth)
    r = client.post("/api/courses", json=post_payload)
    assert r.status_code == 401, r.text

    r = client.put(f"/api/courses/{course.id}", json=put_payload)
    assert r.status_code == 401, r.text

    r = client.delete(f"/api/courses/{course.id}")
    assert r.status_code == 401, r.text