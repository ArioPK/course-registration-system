# backend/tests/test_student_drop_api.py

from datetime import time

import pytest

from backend.app.models.course import Course
from backend.app.models.student import Student
from backend.app.repositories import enrollment_repository
from backend.app.services import unit_limit_service
from backend.app.services.jwt import create_access_token
from backend.tests.test_enrollment_service import _new_id

CURRENT_TERM = "1404-2"


def student_auth_headers(student: Student) -> dict:
    token = create_access_token(data={"sub": student.student_number, "role": "student"})
    return {"Authorization": f"Bearer {token}"}


def professor_auth_headers() -> dict:
    token = create_access_token(data={"sub": "P00001", "role": "professor"})
    return {"Authorization": f"Bearer {token}"}


def _set_unit_policy(db_session, *, min_units: int, max_units: int) -> None:
    policy = unit_limit_service.get_unit_limits_service(db_session)
    policy.min_units = min_units
    policy.max_units = max(max_units, min_units)  # keep DB constraint valid
    db_session.commit()


@pytest.fixture
def student(db_session) -> Student:
    i = _new_id()
    student_number = f"S{i:05d}"
    student = Student(
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
    db_session.add(student)
    db_session.commit()
    return student


@pytest.fixture
def course(db_session) -> Course:
    i = _new_id()
    course = Course(
        code=f"CS{i:03d}",
        name=f"Drop Target {i}",
        capacity=30,
        professor_name="Test Prof",
        day_of_week="MON",
        start_time=time(9, 0),
        end_time=time(10, 0),
        location="Room 101",
        is_active=True,
        units=3,
        department="CS",
        semester=CURRENT_TERM,
    )
    db_session.add(course)
    db_session.commit()
    return course


def test_drop_success_204_and_removed(client, db_session, monkeypatch, student, course):
    monkeypatch.setenv("CURRENT_TERM", CURRENT_TERM)
    _set_unit_policy(db_session, min_units=0, max_units=20)

    enrollment_repository.create(db_session, student_id=student.id, course_id=course.id, term=CURRENT_TERM)

    resp = client.delete(
        f"/api/student/enrollments/{course.id}",
        headers=student_auth_headers(student),
    )

    assert resp.status_code == 204, resp.text
    assert resp.content == b""

    # Enrollment should be removed
    e = enrollment_repository.get_by_student_course_term(db_session, student.id, course.id, CURRENT_TERM)
    assert e is None


def test_drop_not_enrolled_404(client, db_session, monkeypatch, student, course):
    monkeypatch.setenv("CURRENT_TERM", CURRENT_TERM)
    _set_unit_policy(db_session, min_units=0, max_units=20)

    resp = client.delete(
        f"/api/student/enrollments/{course.id}",
        headers=student_auth_headers(student),
    )

    assert resp.status_code == 404, resp.text
    assert resp.json()["detail"] == "Not enrolled in this course"


def test_drop_non_current_term_behavior(client, db_session, monkeypatch, student, course):
    """
    This test assumes the recommended Card 6 behavior:
    drop service looks up enrollment only in CURRENT_TERM.
    Therefore, an enrollment in a past term behaves as "not enrolled" => 404.
    """
    monkeypatch.setenv("CURRENT_TERM", CURRENT_TERM)
    _set_unit_policy(db_session, min_units=0, max_units=20)

    enrollment_repository.create(db_session, student_id=student.id, course_id=course.id, term="1404-1")

    resp = client.delete(
        f"/api/student/enrollments/{course.id}",
        headers=student_auth_headers(student),
    )

    assert resp.status_code == 404, resp.text
    assert resp.json()["detail"] == "Not enrolled in this course"


def test_drop_min_units_violation_409(client, db_session, monkeypatch, student, course):
    monkeypatch.setenv("CURRENT_TERM", CURRENT_TERM)
    _set_unit_policy(db_session, min_units=6, max_units=20)

    # Create a second 3-unit course so student has exactly 6 units
    i = _new_id()
    course2 = Course(
        code=f"CS{i:03d}",
        name=f"Keep {i}",
        capacity=30,
        professor_name="Test Prof",
        day_of_week="TUE",
        start_time=time(11, 0),
        end_time=time(12, 0),
        location="Room 102",
        is_active=True,
        units=3,
        department="CS",
        semester=CURRENT_TERM,
    )
    db_session.add(course2)
    db_session.commit()

    enrollment_repository.create(db_session, student_id=student.id, course_id=course.id, term=CURRENT_TERM)
    enrollment_repository.create(db_session, student_id=student.id, course_id=course2.id, term=CURRENT_TERM)

    resp = client.delete(
        f"/api/student/enrollments/{course.id}",
        headers=student_auth_headers(student),
    )

    assert resp.status_code == 409, resp.text
    assert resp.json()["detail"] == "Dropping would violate minimum units"


def test_drop_auth_no_token_401(client, course):
    resp = client.delete(f"/api/student/enrollments/{course.id}")
    assert resp.status_code == 401, resp.text


def test_drop_auth_role_mismatch_403(client, student, course):
    resp = client.delete(
        f"/api/student/enrollments/{course.id}",
        headers=professor_auth_headers(),
    )
    assert resp.status_code == 403, resp.text