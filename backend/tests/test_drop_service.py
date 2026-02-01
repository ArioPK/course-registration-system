# backend/tests/test_drop_service.py

from __future__ import annotations

import itertools
from datetime import time

import pytest

from backend.app.models.course import Course
from backend.app.models.student import Student
from backend.app.repositories import enrollment_repository
from backend.app.services import unit_limit_service
from backend.app.services.drop_service import (
    drop_student_course,
    NotEnrolledError,
    UnitMinViolationError,
)

_counter = itertools.count(1)


def _new_id() -> int:
    return next(_counter)


def _make_student() -> Student:
    i = _new_id()
    return Student(
        student_number=f"S{i:05d}",
        full_name=f"Student {i}",
        national_id=f"{i:010d}",
        email=f"s{i}@test.local",
        phone_number="09120000000",
        major="CS",
        entry_year=1400,
        units_taken=0,
        password_hash="x",
        is_active=True,
    )


def _make_course(*, term: str, units: int = 3, start_h: int = 9) -> Course:
    i = _new_id()
    return Course(
        code=f"CS{i:03d}",
        name=f"Course {i}",
        capacity=30,
        professor_name="Test Prof",
        day_of_week="MON",
        start_time=time(start_h, 0),
        end_time=time(start_h + 1, 0),
        location="Room 101",
        is_active=True,
        units=units,
        department="CS",
        semester=term,
    )


def _set_policy(db_session, *, min_units: int, max_units: int) -> None:
    """
    Adjust both min and max to avoid CHECK constraint failures (max >= min).
    """
    policy = unit_limit_service.get_unit_limits_service(db_session)
    policy.min_units = min_units
    policy.max_units = max(max_units, min_units)
    db_session.commit()


def test_drop_success(db_session, monkeypatch):
    monkeypatch.setenv("CURRENT_TERM", "1404-1")
    term = "1404-1"

    _set_policy(db_session, min_units=3, max_units=20)

    s = _make_student()
    c1 = _make_course(term=term, units=3, start_h=9)
    c2 = _make_course(term=term, units=3, start_h=11)

    db_session.add_all([s, c1, c2])
    db_session.commit()

    enrollment_repository.create(db_session, student_id=s.id, course_id=c1.id, term=term)
    enrollment_repository.create(db_session, student_id=s.id, course_id=c2.id, term=term)

    # total = 6, after dropping 3 -> 3 (>= min_units=3) OK
    drop_student_course(db_session, student_id=s.id, course_id=c1.id)

    assert enrollment_repository.get_by_student_course_term(db_session, s.id, c1.id, term) is None
    assert enrollment_repository.get_by_student_course_term(db_session, s.id, c2.id, term) is not None


def test_drop_not_enrolled(db_session, monkeypatch):
    monkeypatch.setenv("CURRENT_TERM", "1404-1")
    term = "1404-1"

    _set_policy(db_session, min_units=0, max_units=20)

    s = _make_student()
    c = _make_course(term=term, units=3, start_h=9)

    db_session.add_all([s, c])
    db_session.commit()

    with pytest.raises(NotEnrolledError):
        drop_student_course(db_session, student_id=s.id, course_id=c.id)


def test_drop_non_current_term_scoped_lookup_returns_not_enrolled(db_session, monkeypatch):
    """
    Behavior choice (recommended): drop is scoped to CURRENT_TERM.
    Past-term enrollments are treated as not enrolled for drop.
    """
    monkeypatch.setenv("CURRENT_TERM", "1404-1")
    current_term = "1404-1"
    past_term = "1403-2"

    _set_policy(db_session, min_units=0, max_units=20)

    s = _make_student()
    c = _make_course(term=past_term, units=3, start_h=9)

    db_session.add_all([s, c])
    db_session.commit()

    # enrollment exists, but only in past_term
    enrollment_repository.create(db_session, student_id=s.id, course_id=c.id, term=past_term)

    with pytest.raises(NotEnrolledError):
        drop_student_course(db_session, student_id=s.id, course_id=c.id, term=None)

    # Ensure it did not delete past enrollment
    assert enrollment_repository.get_by_student_course_term(db_session, s.id, c.id, past_term) is not None


def test_drop_min_units_violation(db_session, monkeypatch):
    monkeypatch.setenv("CURRENT_TERM", "1404-1")
    term = "1404-1"

    _set_policy(db_session, min_units=6, max_units=20)

    s = _make_student()
    c1 = _make_course(term=term, units=3, start_h=9)
    c2 = _make_course(term=term, units=3, start_h=11)

    db_session.add_all([s, c1, c2])
    db_session.commit()

    # total units = 6
    enrollment_repository.create(db_session, student_id=s.id, course_id=c1.id, term=term)
    enrollment_repository.create(db_session, student_id=s.id, course_id=c2.id, term=term)

    # dropping 3 => after 3 < min_units 6
    with pytest.raises(UnitMinViolationError):
        drop_student_course(db_session, student_id=s.id, course_id=c1.id)

    # Ensure enrollment still exists (no deletion on failure)
    assert enrollment_repository.get_by_student_course_term(db_session, s.id, c1.id, term) is not None
