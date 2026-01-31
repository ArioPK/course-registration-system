# backend/tests/test_professor_course_students_api.py

from datetime import time

import pytest

from backend.app.models.course import Course
from backend.app.models.student import Student
from backend.app.models.professor import Professor
from backend.app.repositories import enrollment_repository
from backend.app.services.jwt import create_access_token
from backend.tests.test_enrollment_service import _new_id

CURRENT_TERM = "1404-1"


def professor_auth_headers(professor: Professor) -> dict:
    token = create_access_token(data={"sub": professor.professor_code, "role": "professor"})
    return {"Authorization": f"Bearer {token}"}


def student_auth_headers(student: Student) -> dict:
    token = create_access_token(data={"sub": student.student_number, "role": "student"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def professor_p1(db_session) -> Professor:
    i = _new_id()

    data = dict(
        professor_code=f"P{i:05d}",   # keep your project field name
        full_name="Dr. Alice Smith",
        email=f"p{i}@test.local",
        password_hash="x",
        is_active=True,
    )

    # Fill common NOT NULL fields if they exist
    if hasattr(Professor, "national_id"):
        data["national_id"] = f"{i:010d}"
    if hasattr(Professor, "phone_number"):
        data["phone_number"] = "09120000000"
    if hasattr(Professor, "department"):
        data["department"] = "CS"

    p = Professor(**data)
    db_session.add(p)
    db_session.commit()
    return p


@pytest.fixture
def professor_p2(db_session) -> Professor:
    i = _new_id()

    data = dict(
        professor_code=f"P{i:05d}",
        full_name="Dr. Bob Jones",
        email=f"p{i}@test.local",
        password_hash="x",
        is_active=True,
    )

    if hasattr(Professor, "national_id"):
        data["national_id"] = f"{i:010d}"
    if hasattr(Professor, "phone_number"):
        data["phone_number"] = "09120000000"
    if hasattr(Professor, "department"):
        data["department"] = "CS"

    p = Professor(**data)
    db_session.add(p)
    db_session.commit()
    return p


def _make_student(db_session, *, full_name: str) -> Student:
    i = _new_id()
    s_num = f"S{i:05d}"

    data = dict(
        student_number=s_num,
        full_name=full_name,
        email=f"{s_num}@test.local",
        password_hash="x",
        is_active=True,
    )

    # Fill common NOT NULL fields if they exist
    if hasattr(Student, "national_id"):
        data["national_id"] = f"{i:010d}"
    if hasattr(Student, "phone_number"):
        data["phone_number"] = "09120000000"
    if hasattr(Student, "major"):
        data["major"] = "CS"
    if hasattr(Student, "entry_year"):
        data["entry_year"] = 1400
    if hasattr(Student, "units_taken"):
        data["units_taken"] = 0

    s = Student(**data)
    db_session.add(s)
    db_session.commit()
    return s


def _make_course(db_session, *, code: str, professor_name: str) -> Course:
    data = dict(
        code=code,
        name=f"Course {code}",
        capacity=30,
        professor_name=professor_name,
        day_of_week="MON",
        start_time=time(9, 0),
        end_time=time(10, 0),
        location="Room 101",
        is_active=True,
        units=3,
    )

    # term/semester field (match whatever your model uses)
    if hasattr(Course, "semester"):
        data["semester"] = CURRENT_TERM
    elif hasattr(Course, "term"):
        data["term"] = CURRENT_TERM
    else:
        # fallback (if your project uses another name)
        data["semester"] = CURRENT_TERM

    # department field (THIS is the failing NOT NULL)
    if hasattr(Course, "department"):
        data["department"] = "CS"
    elif hasattr(Course, "department_name"):
        data["department_name"] = "CS"
    elif hasattr(Course, "dept"):
        data["dept"] = "CS"
    else:
        # last resort: keep old behavior, but this should not happen in your schema
        data["department"] = "CS"

    c = Course(**data)
    db_session.add(c)
    db_session.commit()
    return c



def test_students_sorted_by_last_name_then_first_name(client, db_session, monkeypatch, professor_p1):
    monkeypatch.setenv("CURRENT_TERM", CURRENT_TERM)

    course = _make_course(db_session, code="CS101", professor_name="Dr. Alice Smith")

    s1 = _make_student(db_session, full_name="Ali Zare")
    s2 = _make_student(db_session, full_name="Sara Ahmadi")
    s3 = _make_student(db_session, full_name="Reza Ahmadi")

    enrollment_repository.create(db_session, student_id=s1.id, course_id=course.id, term=CURRENT_TERM)
    enrollment_repository.create(db_session, student_id=s2.id, course_id=course.id, term=CURRENT_TERM)
    enrollment_repository.create(db_session, student_id=s3.id, course_id=course.id, term=CURRENT_TERM)

    resp = client.get(
        f"/api/professor/courses/{course.id}/students",
        headers=professor_auth_headers(professor_p1),
    )

    assert resp.status_code == 200, resp.text
    body = resp.json()

    assert body["course_id"] == course.id
    assert body["term"] == CURRENT_TERM

    students = body["students"]
    assert [s["full_name"] for s in students] == [
        "Reza Ahmadi",
        "Sara Ahmadi",
        "Ali Zare",
    ]


def test_professor_cannot_view_other_professors_course_403(client, db_session, monkeypatch, professor_p1, professor_p2):
    monkeypatch.setenv("CURRENT_TERM", CURRENT_TERM)

    course = _make_course(db_session, code="CS201", professor_name="Dr. Alice Smith")

    resp = client.get(
        f"/api/professor/courses/{course.id}/students",
        headers=professor_auth_headers(professor_p2),
    )

    assert resp.status_code == 403, resp.text


def test_course_not_found_404(client, monkeypatch, professor_p1):
    monkeypatch.setenv("CURRENT_TERM", CURRENT_TERM)

    resp = client.get(
        "/api/professor/courses/999999/students",
        headers=professor_auth_headers(professor_p1),
    )

    assert resp.status_code == 404, resp.text
    assert resp.json()["detail"] == "The requested course was not found."


def test_auth_no_token_401(client):
    resp = client.get("/api/professor/courses/1/students")
    assert resp.status_code == 401, resp.text


def test_auth_role_mismatch_student_403(client, db_session, monkeypatch, professor_p1):
    monkeypatch.setenv("CURRENT_TERM", CURRENT_TERM)

    course = _make_course(db_session, code="CS101", professor_name="Dr. Alice Smith")
    s = _make_student(db_session, full_name="Student One")

    resp = client.get(
        f"/api/professor/courses/{course.id}/students",
        headers=student_auth_headers(s),
    )

    assert resp.status_code == 403, resp.text