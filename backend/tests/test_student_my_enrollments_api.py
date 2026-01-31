# backend/tests/test_student_my_enrollments_api.py

from __future__ import annotations

from datetime import time

import pytest

from backend.app.models.course import Course
from backend.app.models.professor import Professor
from backend.app.models.student import Student
from backend.app.services.jwt import create_access_token
from backend.tests.test_enrollment_service import _new_id

from backend.app.models.enrollment import Enrollment  


def student_headers(student: Student) -> dict:
    token = create_access_token(data={"sub": student.student_number, "role": "student"})
    return {"Authorization": f"Bearer {token}"}


def professor_headers(professor: Professor) -> dict:
    # your tests use professor_code
    token = create_access_token(data={"sub": professor.professor_code, "role": "professor"})
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


@pytest.fixture
def professor(db_session) -> Professor:
    i = _new_id()
    professor_code = f"P{i:05d}"
    p = Professor(
        professor_code=professor_code,
        full_name="Prof Test",
        email=f"{professor_code}@test.local",
        password_hash="x",
        is_active=True,
    )
    db_session.add(p)
    db_session.commit()
    return p


def _mk_course(db_session, *, code: str, professor: Professor, term: str, day: str, start: time) -> Course:
    c = Course(
        code=code,
        name=f"{code} Name",
        capacity=30,
        professor_name=professor.full_name,
        day_of_week=day,
        start_time=start,
        end_time=time(start.hour + 1, start.minute),
        location="Room 101",
        is_active=True,
        units=3,
        department="CS",
        semester=term,
    )
    db_session.add(c)
    db_session.commit()
    return c


def _enroll(db_session, *, student_id: int, course_id: int, term: str):
    # support either Enrollment.term or Enrollment.semester
    kwargs = {"student_id": student_id, "course_id": course_id}
    if hasattr(Enrollment, "term"):
        kwargs["term"] = term
    else:
        kwargs["semester"] = term

    e = Enrollment(**kwargs)
    db_session.add(e)
    db_session.commit()
    db_session.refresh(e)
    return e


def test_my_enrollments_happy_path_scoped_to_current_term(client, db_session, monkeypatch, student, professor):
    current_term = "1404-1"
    monkeypatch.setenv("CURRENT_TERM", current_term)

    headers = student_headers(student)

    c1 = _mk_course(db_session, code="CS101", professor=professor, term=current_term, day="MON", start=time(9, 0))
    c2 = _mk_course(db_session, code="CS102", professor=professor, term=current_term, day="MON", start=time(11, 0))

    old_term = "1403-2"
    cold = _mk_course(db_session, code="CS099", professor=professor, term=old_term, day="SUN", start=time(8, 0))

    _enroll(db_session, student_id=student.id, course_id=c1.id, term=current_term)
    _enroll(db_session, student_id=student.id, course_id=c2.id, term=current_term)
    _enroll(db_session, student_id=student.id, course_id=cold.id, term=old_term)

    r = client.get("/api/student/enrollments", headers=headers)
    assert r.status_code == 200, r.text

    data = r.json()
    assert isinstance(data, list)
    assert len(data) == 2

    for item in data:
        assert item["term"] == current_term
        assert item["created_at"]
        assert "course" in item
        assert item["course"]["id"]
        assert item["course"]["code"]


def test_my_enrollments_sorting_by_day_then_time(client, db_session, monkeypatch, student, professor):
    current_term = "1404-1"
    monkeypatch.setenv("CURRENT_TERM", current_term)

    headers = student_headers(student)

    c_sun = _mk_course(db_session, code="CS200", professor=professor, term=current_term, day="SUN", start=time(10, 0))
    c_mon_early = _mk_course(db_session, code="CS201", professor=professor, term=current_term, day="MON", start=time(9, 0))
    c_mon_late = _mk_course(db_session, code="CS202", professor=professor, term=current_term, day="MON", start=time(11, 0))

    _enroll(db_session, student_id=student.id, course_id=c_mon_late.id, term=current_term)
    _enroll(db_session, student_id=student.id, course_id=c_sun.id, term=current_term)
    _enroll(db_session, student_id=student.id, course_id=c_mon_early.id, term=current_term)

    r = client.get("/api/student/enrollments", headers=headers)
    assert r.status_code == 200, r.text
    data = r.json()

    codes = [item["course"]["code"] for item in data]
    assert codes == ["CS200", "CS201", "CS202"]


def test_my_enrollments_auth_boundaries(client, monkeypatch, student, professor):
    monkeypatch.setenv("CURRENT_TERM", "1404-1")

    # no token -> 401
    r = client.get("/api/student/enrollments")
    assert r.status_code == 401, r.text

    # professor token -> 403
    r = client.get("/api/student/enrollments", headers=professor_headers(professor))
    assert r.status_code == 403, r.text