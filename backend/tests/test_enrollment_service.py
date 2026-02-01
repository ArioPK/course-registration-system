# backend/tests/test_enrollment_service.py

from __future__ import annotations

import itertools
from datetime import time

import pytest

from backend.app.models.student import Student
from backend.app.models.course import Course
from backend.app.models.course_prerequisite import CoursePrerequisite

from backend.app.repositories import enrollment_repository, course_history_repository
from backend.app.services import unit_limit_service
from backend.app.services.enrollment_service import (
    enroll_student,
    PrereqNotMetError,
    TimeConflictError,
    CapacityFullError,
    DuplicateEnrollmentError,
    UnitLimitViolationError,
    CourseNotFoundError,
)

_counter = itertools.count(1)


def _new_id() -> int:
    return next(_counter)


def _make_student() -> Student:
    i = _new_id()
    national_id = f"{i:010d}"  # UNIQUE, 10 digits
    student_number = f"S{i:05d}"

    return Student(
        student_number=student_number,
        full_name=f"Student {i}",
        national_id=national_id,
        email=f"{student_number}@test.local",
        phone_number="09120000000",
        major="CS",
        entry_year=1400,
        units_taken=0,
        password_hash="x",
        is_active=True,
    )


def _make_course(
    *,
    units: int = 3,
    capacity: int = 30,
    day_of_week: str = "MON",
    start: time = time(9, 0),
    end: time = time(10, 0),
) -> Course:
    i = _new_id()
    return Course(
        code=f"CE{i:03d}",
        name=f"Course {i}",
        capacity=capacity,
        professor_name="Test Prof",
        day_of_week=day_of_week,  # SAT/SUN/MON/TUE/WED/THU/FRI
        start_time=start,
        end_time=end,
        location="Room 101",
        is_active=True,
        units=units,
        department="CS",
        semester="1404-1",
    )


def _set_max_units(db_session, max_units: int) -> None:
    policy = unit_limit_service.get_unit_limits_service(db_session)
    policy.max_units = max_units

    # Keep DB constraint valid: max_units must be >= min_units
    if policy.min_units > max_units:
        policy.min_units = max_units

    db_session.commit()

def _add_prereq_link(db_session, *, course_id: int, prereq_course_id: int) -> None:
    """
    Create a CoursePrerequisite row using the actual column names in this codebase.

    Your error indicates the model uses: prereq_course_id
    This helper also supports alternative column names if they exist.
    """
    kwargs = {"course_id": course_id}

    if hasattr(CoursePrerequisite, "prereq_course_id"):
        kwargs["prereq_course_id"] = prereq_course_id
    elif hasattr(CoursePrerequisite, "prerequisite_course_id"):
        kwargs["prerequisite_course_id"] = prereq_course_id
    elif hasattr(CoursePrerequisite, "prerequisite_id"):
        kwargs["prerequisite_id"] = prereq_course_id
    else:
        raise RuntimeError(
            "CoursePrerequisite does not expose a recognized prereq FK column "
            "(expected one of: prereq_course_id, prerequisite_course_id, prerequisite_id)."
        )

    link = CoursePrerequisite(**kwargs)
    db_session.add(link)
    db_session.commit()


def test_enroll_student_happy_path(db_session):
    term = "1404-1"
    _set_max_units(db_session, 20)

    s = _make_student()
    prereq = _make_course(units=3)
    target = _make_course(units=3)

    db_session.add_all([s, prereq, target])
    db_session.commit()

    _add_prereq_link(db_session, course_id=target.id, prereq_course_id=prereq.id)

    course_history_repository.create_history_record(
        db_session,
        student_id=s.id,
        course_id=prereq.id,
        term="1403-2",
        status="passed",
        grade=18.0,
    )

    e = enroll_student(db_session, student_id=s.id, course_id=target.id, term=term)
    assert e.student_id == s.id
    assert e.course_id == target.id
    assert e.term == term


def test_enroll_student_missing_prereq(db_session):
    term = "1404-1"
    _set_max_units(db_session, 20)

    s = _make_student()
    prereq = _make_course(units=3)
    target = _make_course(units=3)

    db_session.add_all([s, prereq, target])
    db_session.commit()

    _add_prereq_link(db_session, course_id=target.id, prereq_course_id=prereq.id)

    with pytest.raises(PrereqNotMetError):
        enroll_student(db_session, student_id=s.id, course_id=target.id, term=term)


def test_enroll_student_time_conflict(db_session):
    term = "1404-1"
    _set_max_units(db_session, 20)

    s = _make_student()
    existing = _make_course(day_of_week="MON", start=time(9, 0), end=time(10, 0), units=2)
    new_course = _make_course(day_of_week="MON", start=time(9, 30), end=time(10, 30), units=2)

    db_session.add_all([s, existing, new_course])
    db_session.commit()

    enrollment_repository.create(db_session, student_id=s.id, course_id=existing.id, term=term)

    with pytest.raises(TimeConflictError):
        enroll_student(db_session, student_id=s.id, course_id=new_course.id, term=term)


def test_enroll_student_capacity_full(db_session):
    term = "1404-1"
    _set_max_units(db_session, 20)

    s1 = _make_student()
    s2 = _make_student()
    course = _make_course(units=3, capacity=1)

    db_session.add_all([s1, s2, course])
    db_session.commit()

    enrollment_repository.create(db_session, student_id=s1.id, course_id=course.id, term=term)

    with pytest.raises(CapacityFullError):
        enroll_student(db_session, student_id=s2.id, course_id=course.id, term=term)


def test_enroll_student_duplicate(db_session):
    term = "1404-1"
    _set_max_units(db_session, 20)

    s = _make_student()
    course = _make_course(units=3)

    db_session.add_all([s, course])
    db_session.commit()

    enroll_student(db_session, student_id=s.id, course_id=course.id, term=term)

    with pytest.raises(DuplicateEnrollmentError):
        enroll_student(db_session, student_id=s.id, course_id=course.id, term=term)


def test_enroll_student_units_exceed_max(db_session):
    term = "1404-1"

    # Get the existing policy; must keep max_units >= min_units
    policy = unit_limit_service.get_unit_limits_service(db_session)
    min_units = getattr(policy, "min_units", 0) or 0

    # Smallest valid max that won't violate CHECK constraint
    policy.max_units = max(1, min_units)
    db_session.commit()

    max_units = policy.max_units

    s = _make_student()
    db_session.add(s)
    db_session.commit()

    # Fill the term to exactly max_units, then try adding 1 more unit
    units_left = max_units
    hour = 8
    taken_courses = []

    while units_left > 0:
        u = 3 if units_left >= 3 else units_left  # keep units small (<=3)
        c = _make_course(units=u, start=time(hour, 0), end=time(hour + 1, 0))
        taken_courses.append(c)
        units_left -= u
        hour += 1

    c_new = _make_course(units=1, start=time(hour, 0), end=time(hour + 1, 0))

    db_session.add_all(taken_courses + [c_new])
    db_session.commit()

    for c in taken_courses:
        enrollment_repository.create(db_session, student_id=s.id, course_id=c.id, term=term)

    with pytest.raises(UnitLimitViolationError):
        enroll_student(db_session, student_id=s.id, course_id=c_new.id, term=term)


def test_enroll_student_course_not_found(db_session):
    with pytest.raises(CourseNotFoundError):
        enroll_student(db_session, student_id=123, course_id=999999, term="1404-1")