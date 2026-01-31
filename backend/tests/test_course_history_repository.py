# backend/tests/test_course_history_repository.py

from datetime import time

from backend.app.models.student import Student
from backend.app.models.course import Course
from backend.app.repositories import course_history_repository
from backend.app.models.enrollment import Enrollment  # noqa: F401


def _make_student(student_number: str, full_name: str, national_id: str) -> Student:
    return Student(
        student_number=student_number,
        full_name=full_name,
        national_id=national_id,
        email=f"{student_number}@test.local",
        phone_number="09120000000",
        major="CS",
        entry_year=1400,
        units_taken=0,
        password_hash="x",
        is_active=True,
    )


def _make_course(code: str, name: str, units: int) -> Course:
    # day_of_week must match your API enum: SAT/SUN/MON/TUE/WED/THU/FRI
    # keep units <= 4 to avoid schema validation constraints in some codebases
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
        units=units,
        department="CS",
        semester="1",
    )


def test_has_passed_course_strict_status(db_session):
    s = _make_student("6001", "Student One", "1111111111")
    c1 = _make_course("CE301", "Algorithms", units=3)

    db_session.add_all([s, c1])
    db_session.commit()

    # no history yet
    assert course_history_repository.has_passed_course(db_session, s.id, c1.id) is False

    # failed does not count
    course_history_repository.create_history_record(
        db_session,
        student_id=s.id,
        course_id=c1.id,
        term="1404-1",
        status="failed",
        grade=10.0,
    )
    assert course_history_repository.has_passed_course(db_session, s.id, c1.id) is False

    # passed counts
    course_history_repository.create_history_record(
        db_session,
        student_id=s.id,
        course_id=c1.id,
        term="1404-2",
        status="passed",
        grade=17.5,
    )
    assert course_history_repository.has_passed_course(db_session, s.id, c1.id) is True


def test_list_passed_courses_returns_only_passed(db_session):
    s = _make_student("6002", "Student Two", "2222222222")
    c1 = _make_course("CE302", "Databases", units=3)
    c2 = _make_course("CE303", "Networks", units=4)

    db_session.add_all([s, c1, c2])
    db_session.commit()

    assert course_history_repository.list_passed_courses(db_session, s.id) == []

    # one failed, one passed
    course_history_repository.create_history_record(
        db_session,
        student_id=s.id,
        course_id=c1.id,
        term="1404-1",
        status="failed",
    )
    course_history_repository.create_history_record(
        db_session,
        student_id=s.id,
        course_id=c2.id,
        term="1404-1",
        status="passed",
    )

    passed_ids = course_history_repository.list_passed_courses(db_session, s.id)
    assert passed_ids == [c2.id]