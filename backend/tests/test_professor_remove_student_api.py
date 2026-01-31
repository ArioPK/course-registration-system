from datetime import time

import pytest

from backend.app.models.course import Course
from backend.app.models.professor import Professor
from backend.app.models.student import Student
from backend.app.repositories import enrollment_repository
from backend.app.services.jwt import create_access_token
from backend.tests.test_enrollment_service import _new_id

CURRENT_TERM = "1404-1"
OTHER_TERM = "1404-2"


def professor_auth_headers(professor: Professor) -> dict:
    token = create_access_token(data={"sub": professor.professor_code, "role": "professor"})
    return {"Authorization": f"Bearer {token}"}


def student_auth_headers(student: Student) -> dict:
    token = create_access_token(data={"sub": student.student_number, "role": "student"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def professor_p1(db_session) -> Professor:
    i = _new_id()
    p = Professor(
        professor_code=f"P{i:05d}",
        full_name="Dr. Alice Smith",
        # national_id=f"{i:010d}",
        email=f"p{i}@test.local",
        # phone_number="09120000000",
        # department="CS",
        password_hash="x",
        is_active=True,
    )
    db_session.add(p)
    db_session.commit()
    return p


@pytest.fixture
def professor_p2(db_session) -> Professor:
    i = _new_id()
    p = Professor(
        professor_code=f"P{i:05d}",
        full_name="Dr. Bob Jones",
        # national_id=f"{i:010d}",
        email=f"p{i}@test.local",
        # phone_number="09120000000",
        # department="CS",
        password_hash="x",
        is_active=True,
    )
    db_session.add(p)
    db_session.commit()
    return p


def _make_course(db_session, *, code: str, professor_name: str, semester: str) -> Course:
    c = Course(
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
        department="CS",
        semester=semester,
    )
    db_session.add(c)
    db_session.commit()
    return c


def _make_student(db_session, *, full_name: str) -> Student:
    i = _new_id()
    s_num = f"S{i:05d}"
    s = Student(
        student_number=s_num,
        full_name=full_name,
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


def test_remove_student_success_204_and_deleted(client, db_session, monkeypatch, professor_p1):
    monkeypatch.setenv("CURRENT_TERM", CURRENT_TERM)

    course = _make_course(db_session, code="CS101", professor_name="Dr. Alice Smith", semester=CURRENT_TERM)
    student = _make_student(db_session, full_name="Student One")

    enrollment_repository.create(db_session, student_id=student.id, course_id=course.id, term=CURRENT_TERM)

    resp = client.delete(
        f"/api/professor/courses/{course.id}/students/{student.id}",
        headers=professor_auth_headers(professor_p1),
    )

    assert resp.status_code == 204, resp.text
    assert resp.content == b""

    e = enrollment_repository.get_by_student_course_term(db_session, student.id, course.id, CURRENT_TERM)
    assert e is None


def test_remove_student_wrong_owner_403(client, db_session, monkeypatch, professor_p1, professor_p2):
    monkeypatch.setenv("CURRENT_TERM", CURRENT_TERM)

    course = _make_course(db_session, code="CS201", professor_name="Dr. Alice Smith", semester=CURRENT_TERM)
    student = _make_student(db_session, full_name="Student One")
    enrollment_repository.create(db_session, student_id=student.id, course_id=course.id, term=CURRENT_TERM)

    resp = client.delete(
        f"/api/professor/courses/{course.id}/students/{student.id}",
        headers=professor_auth_headers(professor_p2),
    )

    assert resp.status_code == 403, resp.text


def test_remove_student_non_current_term_enrollment_409(client, db_session, monkeypatch, professor_p1):
    # current term is OTHER_TERM, but enrollment exists in CURRENT_TERM => must be 409
    monkeypatch.setenv("CURRENT_TERM", OTHER_TERM)

    course = _make_course(db_session, code="CS301", professor_name="Dr. Alice Smith", semester=CURRENT_TERM)
    student = _make_student(db_session, full_name="Student One")
    enrollment_repository.create(db_session, student_id=student.id, course_id=course.id, term=CURRENT_TERM)

    resp = client.delete(
        f"/api/professor/courses/{course.id}/students/{student.id}",
        headers=professor_auth_headers(professor_p1),
    )

    assert resp.status_code == 409, resp.text


def test_remove_student_enrollment_not_found_404(client, db_session, monkeypatch, professor_p1):
    monkeypatch.setenv("CURRENT_TERM", CURRENT_TERM)

    course = _make_course(db_session, code="CS401", professor_name="Dr. Alice Smith", semester=CURRENT_TERM)
    student = _make_student(db_session, full_name="Student One")

    resp = client.delete(
        f"/api/professor/courses/{course.id}/students/{student.id}",
        headers=professor_auth_headers(professor_p1),
    )

    assert resp.status_code == 404, resp.text


def test_remove_student_auth_no_token_401(client):
    resp = client.delete("/api/professor/courses/1/students/1")
    assert resp.status_code == 401, resp.text


def test_remove_student_auth_role_mismatch_student_403(client, db_session, monkeypatch, professor_p1):
    monkeypatch.setenv("CURRENT_TERM", CURRENT_TERM)

    course = _make_course(db_session, code="CS501", professor_name="Dr. Alice Smith", semester=CURRENT_TERM)
    student = _make_student(db_session, full_name="Student One")
    enrollment_repository.create(db_session, student_id=student.id, course_id=course.id, term=CURRENT_TERM)

    resp = client.delete(
        f"/api/professor/courses/{course.id}/students/{student.id}",
        headers=student_auth_headers(student),
    )

    assert resp.status_code == 403, resp.text