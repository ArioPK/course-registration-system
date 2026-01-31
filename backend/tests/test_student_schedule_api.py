# backend/tests/test_student_schedule_api.py

from datetime import time

import pytest

from backend.app.models.course import Course
from backend.app.models.student import Student
from backend.app.repositories import enrollment_repository
from backend.app.services.jwt import create_access_token
from backend.tests.test_enrollment_service import _new_id

CURRENT_TERM = "1404-1"


def student_auth_headers(student: Student) -> dict:
    token = create_access_token(data={"sub": student.student_number, "role": "student"})
    return {"Authorization": f"Bearer {token}"}


def professor_auth_headers() -> dict:
    token = create_access_token(data={"sub": "P00001", "role": "professor"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def student(db_session) -> Student:
    i = _new_id()
    student_number = f"S{i:05d}"
    s = Student(
        student_number=student_number,
        full_name=f"Student {i}",
        national_id=f"{i:010d}",
        email=f"{student_number}@test.local",
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


def _make_course(db_session, *, code: str, name: str, day: str, start: time, end: time) -> Course:
    c = Course(
        code=code,
        name=name,
        capacity=30,
        professor_name="Test Prof",
        day_of_week=day,
        start_time=start,
        end_time=end,
        location="Room 101",
        is_active=True,
        units=3,
        department="CS",
        semester=CURRENT_TERM,
    )
    db_session.add(c)
    db_session.commit()
    return c


def test_get_student_schedule_success_sorted(client, db_session, monkeypatch, student):
    monkeypatch.setenv("CURRENT_TERM", CURRENT_TERM)

    # Same day, different times to verify sorting
    c1 = _make_course(
        db_session,
        code="CS101",
        name="Earlier",
        day="MON",
        start=time(8, 0),
        end=time(9, 0),
    )
    c2 = _make_course(
        db_session,
        code="CS102",
        name="Later",
        day="MON",
        start=time(9, 0),
        end=time(10, 0),
    )

    enrollment_repository.create(db_session, student_id=student.id, course_id=c1.id, term=CURRENT_TERM)
    enrollment_repository.create(db_session, student_id=student.id, course_id=c2.id, term=CURRENT_TERM)

    resp = client.get(
        "/api/student/schedule",
        headers=student_auth_headers(student),
    )

    assert resp.status_code == 200, resp.text
    body = resp.json()

    assert body["term"] == CURRENT_TERM
    assert isinstance(body["days"], list)

    # Service returns all days (Card 8 requirement)
    assert len(body["days"]) == 7

    # Collect all course_ids across days
    all_course_ids = [b["course_id"] for d in body["days"] for b in d["blocks"]]
    assert c1.id in all_course_ids
    assert c2.id in all_course_ids

    mon = next(d for d in body["days"] if d["day_of_week"] == "MON")
    assert [b["course_id"] for b in mon["blocks"]] == [c1.id, c2.id]


def test_get_student_schedule_auth_no_token_401(client):
    resp = client.get("/api/student/schedule")
    assert resp.status_code == 401, resp.text


def test_get_student_schedule_auth_role_mismatch_403(client):
    resp = client.get("/api/student/schedule", headers=professor_auth_headers())
    assert resp.status_code == 403, resp.text