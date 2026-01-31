# backend/tests/test_enrollment_repository.py

from datetime import time

from backend.app.models.student import Student
from backend.app.models.course import Course
from backend.app.repositories import enrollment_repository


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


def _make_course(code: str, name: str, units: int, *, is_active: bool = False) -> Course:
    """
    Important:
    - Response schema in course catalog enforces units <= 4, so tests must not create units > 4.
    - Keep these repository-test courses inactive so they don't appear in student catalog endpoints.
    """
    if units < 0 or units > 4:
        raise ValueError("Test course units must be between 0 and 4 (inclusive) to satisfy API schema constraints.")

    return Course(
        code=code,
        name=name,
        capacity=30,
        professor_name="Test Prof",
        day_of_week="MON",       # must match enum: SAT/SUN/MON/TUE/WED/THU/FRI
        start_time=time(9, 0),
        end_time=time(10, 0),
        location="Room 101",
        is_active=is_active,
        units=units,
        department="CS",
        semester="1",
    )


def test_get_by_student_course_term(db_session):
    term = "1404-1"
    other_term = "1404-2"

    s = _make_student("5001", "Student One", "0011111111")
    c1 = _make_course("CE201", "Course 1", units=3)

    db_session.add_all([s, c1])
    db_session.commit()

    assert enrollment_repository.get_by_student_course_term(db_session, s.id, c1.id, term) is None

    e = enrollment_repository.create(db_session, student_id=s.id, course_id=c1.id, term=term)

    found = enrollment_repository.get_by_student_course_term(db_session, s.id, c1.id, term)
    assert found is not None
    assert found.id == e.id

    assert enrollment_repository.get_by_student_course_term(db_session, s.id, c1.id, other_term) is None


def test_count_course_enrollments_term_scoped(db_session):
    term = "1404-1"
    other_term = "1404-2"

    s1 = _make_student("5002", "Student A", "0022222222")
    s2 = _make_student("5003", "Student B", "0033333333")
    c1 = _make_course("CE202", "Course 2", units=3)

    db_session.add_all([s1, s2, c1])
    db_session.commit()

    enrollment_repository.create(db_session, student_id=s1.id, course_id=c1.id, term=term)
    enrollment_repository.create(db_session, student_id=s2.id, course_id=c1.id, term=term)
    enrollment_repository.create(db_session, student_id=s1.id, course_id=c1.id, term=other_term)

    assert enrollment_repository.count_course_enrollments(db_session, c1.id, term) == 2
    assert enrollment_repository.count_course_enrollments(db_session, c1.id, other_term) == 1


def test_list_student_enrollments_term_scoped_and_ordered(db_session):
    term = "1404-1"
    other_term = "1404-2"

    s = _make_student("5004", "Student C", "0044444444")
    c1 = _make_course("CE203", "Course 3", units=2)
    c2 = _make_course("CE204", "Course 4", units=4)

    db_session.add_all([s, c1, c2])
    db_session.commit()

    e1 = enrollment_repository.create(db_session, student_id=s.id, course_id=c1.id, term=term)
    e2 = enrollment_repository.create(db_session, student_id=s.id, course_id=c2.id, term=term)
    enrollment_repository.create(db_session, student_id=s.id, course_id=c1.id, term=other_term)

    rows = enrollment_repository.list_student_enrollments(db_session, s.id, term)
    assert [r.id for r in rows] == sorted([e1.id, e2.id])


def test_sum_student_units_returns_total_and_zero_when_none(db_session):
    term = "1404-1"
    other_term = "1404-2"

    s = _make_student("5005", "Student D", "0055555555")
    c1 = _make_course("CE205", "Course 5", units=3)
    c2 = _make_course("CE206", "Course 6", units=4)  # was 5 -> invalid for schema

    db_session.add_all([s, c1, c2])
    db_session.commit()

    assert enrollment_repository.sum_student_units(db_session, s.id, term) == 0

    enrollment_repository.create(db_session, student_id=s.id, course_id=c1.id, term=term)
    enrollment_repository.create(db_session, student_id=s.id, course_id=c2.id, term=term)
    enrollment_repository.create(db_session, student_id=s.id, course_id=c2.id, term=other_term)

    assert enrollment_repository.sum_student_units(db_session, s.id, term) == 7
    assert enrollment_repository.sum_student_units(db_session, s.id, other_term) == 4


def test_list_course_enrollments_term_scoped(db_session):
    term = "1404-1"
    other_term = "1404-2"

    s1 = _make_student("5006", "Student E", "0066666666")
    s2 = _make_student("5007", "Student F", "0077777777")
    c = _make_course("CE207", "Course 7", units=3)

    db_session.add_all([s1, s2, c])
    db_session.commit()

    e1 = enrollment_repository.create(db_session, student_id=s1.id, course_id=c.id, term=term)
    e2 = enrollment_repository.create(db_session, student_id=s2.id, course_id=c.id, term=term)
    enrollment_repository.create(db_session, student_id=s1.id, course_id=c.id, term=other_term)

    rows = enrollment_repository.list_course_enrollments(db_session, c.id, term)
    assert [r.id for r in rows] == sorted([e1.id, e2.id])


def test_delete_removes_row(db_session):
    term = "1404-1"

    s = _make_student("5008", "Student G", "0088888888")
    c = _make_course("CE208", "Course 8", units=3)

    db_session.add_all([s, c])
    db_session.commit()

    e = enrollment_repository.create(db_session, student_id=s.id, course_id=c.id, term=term)
    assert enrollment_repository.get_by_student_course_term(db_session, s.id, c.id, term) is not None

    enrollment_repository.delete(db_session, e)
    assert enrollment_repository.get_by_student_course_term(db_session, s.id, c.id, term) is None