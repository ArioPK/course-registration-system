# backend/tests/test_schedule_service.py

from datetime import time

import pytest

from backend.app.models.course import Course
from backend.app.models.student import Student
from backend.app.repositories import enrollment_repository
from backend.app.schemas.schedule import WeeklyScheduleRead
from backend.app.services.schedule_service import build_weekly_schedule
from backend.tests.test_enrollment_service import _new_id

CURRENT_TERM = "1404-1"
OTHER_TERM = "1404-2"


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
        name=f"Test Course {i}",
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


def test_build_weekly_schedule_grouping_and_sorting(db_session, monkeypatch, student, course):
    monkeypatch.setenv("CURRENT_TERM", CURRENT_TERM)

    # Another course on the same day, earlier time => should sort before `course`
    i = _new_id()
    course2 = Course(
        code=f"CS{i:03d}",
        name=f"Earlier Course {i}",
        capacity=30,
        professor_name="Test Prof",
        day_of_week="MON",
        start_time=time(8, 0),
        end_time=time(9, 0),
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

    schedule = build_weekly_schedule(db_session, student_id=student.id)  # uses CURRENT_TERM env

    assert isinstance(schedule, WeeklyScheduleRead)
    assert schedule.term == CURRENT_TERM

    # Card 8 requirement: do not skip days
    assert len(schedule.days) == 7

    mon = next(d for d in schedule.days if d.day_of_week == "MON")
    assert [b.course_id for b in mon.blocks] == [course2.id, course.id]  # sorted by start_time


def test_filter_by_current_term(db_session, monkeypatch, student, course):
    monkeypatch.setenv("CURRENT_TERM", CURRENT_TERM)

    # Enrollment in CURRENT_TERM (should appear)
    enrollment_repository.create(db_session, student_id=student.id, course_id=course.id, term=CURRENT_TERM)

    # Enrollment in OTHER_TERM (should NOT appear)
    i = _new_id()
    other_course = Course(
        code=f"CS{i:03d}",
        name=f"Other Term Course {i}",
        capacity=30,
        professor_name="Other Prof",
        day_of_week="TUE",
        start_time=time(10, 0),
        end_time=time(11, 0),
        location="Room 201",
        is_active=True,
        units=3,
        department="CS",
        semester=OTHER_TERM,
    )
    db_session.add(other_course)
    db_session.commit()

    enrollment_repository.create(db_session, student_id=student.id, course_id=other_course.id, term=OTHER_TERM)

    schedule = build_weekly_schedule(db_session, student_id=student.id)  # uses CURRENT_TERM env

    # Card 8: do not skip days
    assert len(schedule.days) == 7

    # Only CURRENT_TERM enrollment is present
    all_ids = [b.course_id for day in schedule.days for b in day.blocks]
    assert course.id in all_ids
    assert other_course.id not in all_ids


def test_no_enrollments_returns_all_days_empty(db_session, monkeypatch, student):
    monkeypatch.setenv("CURRENT_TERM", CURRENT_TERM)

    schedule = build_weekly_schedule(db_session, student_id=student.id)

    assert schedule.term == CURRENT_TERM
    assert len(schedule.days) == 7
    assert all(len(day.blocks) == 0 for day in schedule.days)