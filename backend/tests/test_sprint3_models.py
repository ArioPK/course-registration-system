# backend/tests/test_sprint3_models.py

import pytest
from datetime import time

from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError

from backend.app.models.enrollment import Enrollment
from backend.app.models.student_course_history import StudentCourseHistory
from backend.app.models.student import Student
from backend.app.models.course import Course


def _make_student(student_number: str, full_name: str, national_id: str) -> Student:
    """
    Your schema has NOT NULL on students.national_id (per failing traceback).
    We also set other common fields to avoid future NOT NULL errors.
    Adjust only if your Student model has different required fields.
    """
    return Student(
        student_number=student_number,
        full_name=full_name,
        national_id=national_id,                 # ✅ required (NOT NULL)
        email=f"{student_number}@test.local",    # safe even if nullable
        phone_number="09120000000",              # safe even if nullable
        major="CS",                              # safe even if nullable
        entry_year=1400,                         # safe even if nullable
        units_taken=0,                           # your insert shows units_taken exists
        mark=None,
        password_hash="x",
        is_active=True,
    )


def _make_course(code: str, name: str) -> Course:
    """
    Your schema has NOT NULL on:
      - professor_name
      - day_of_week
    Likely also start_time/end_time/location, so we set them too.
    """
    return Course(
        code=code,
        name=name,
        capacity=30,
        professor_name="Test Prof",
        day_of_week="MON",
        start_time=time(9, 0),
        end_time=time(10, 0),
        location="Room 101",
        is_active=True,
        units=3,
        department="CS",
        semester="1",
    )


def test_tables_exist(db_session):
    inspector = inspect(db_session.bind)
    tables = set(inspector.get_table_names())

    assert "enrollments" in tables
    assert "student_course_history" in tables


def test_unique_constraints_exist(db_session):
    inspector = inspect(db_session.bind)

    enroll_uq = inspector.get_unique_constraints("enrollments")
    assert any(
        set(uq["column_names"]) == {"student_id", "course_id", "term"}
        for uq in enroll_uq
    ), f"Expected UQ (student_id, course_id, term) on enrollments. Found: {enroll_uq}"

    hist_uq = inspector.get_unique_constraints("student_course_history")
    assert any(
        set(uq["column_names"]) == {"student_id", "course_id", "term"}
        for uq in hist_uq
    ), f"Expected UQ (student_id, course_id, term) on student_course_history. Found: {hist_uq}"


def test_enrollment_unique_constraint(db_session):
    s = _make_student("4001", "Ali Test", national_id="0012345678")
    c = _make_course("CE101", "Intro")

    db_session.add_all([s, c])
    db_session.commit()

    e1 = Enrollment(student_id=s.id, course_id=c.id, term="1404-1")
    db_session.add(e1)
    db_session.commit()

    # Duplicate must fail
    e2 = Enrollment(student_id=s.id, course_id=c.id, term="1404-1")
    db_session.add(e2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_course_history_unique_constraint(db_session):
    s = _make_student("4002", "Sara Test", national_id="0098765432")
    c = _make_course("CE102", "Math")

    db_session.add_all([s, c])
    db_session.commit()

    h1 = StudentCourseHistory(
        student_id=s.id,
        course_id=c.id,
        term="1404-1",
        status="passed",
        grade=18.5,
    )
    db_session.add(h1)
    db_session.commit()

    # Duplicate must fail
    h2 = StudentCourseHistory(
        student_id=s.id,
        course_id=c.id,
        term="1404-1",
        status="passed",
        grade=19.0,
    )
    db_session.add(h2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()