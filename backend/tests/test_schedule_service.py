# backend/tests/test_schedule_service.py

from datetime import time

import pytest

from backend.app.models.course import Course
from backend.app.models.student import Student
from backend.app.repositories import enrollment_repository
from backend.app.schemas.schedule import WeeklyScheduleRead
from backend.app.services.schedule_service import build_weekly_schedule
from backend.tests import factories

OTHER_TERM = "1404-2"


@pytest.fixture
def student(db_session) -> Student:
    return factories.make_student(db_session)


@pytest.fixture
def course(db_session, current_term) -> Course:
    return factories.make_course(
        db_session,
        semester=current_term,
        professor_name="Test Prof",
        day_of_week="MON",
        start_time=time(9, 0),
        end_time=time(10, 0),
        location="Room 101",
    )


def test_build_weekly_schedule_grouping_and_sorting(db_session, current_term, student, course):
    # Another course on the same day, earlier time => should sort before `course`
    course2 = factories.make_course(
        db_session,
        semester=current_term,
        professor_name="Test Prof",
        day_of_week="MON",
        start_time=time(8, 0),
        end_time=time(9, 0),
        location="Room 102",
    )

    factories.add_enrollment(db_session, student_id=student.id, course_id=course.id, term=current_term)
    factories.add_enrollment(db_session, student_id=student.id, course_id=course2.id, term=current_term)

    schedule = build_weekly_schedule(db_session, student_id=student.id)  # uses CURRENT_TERM env

    assert isinstance(schedule, WeeklyScheduleRead)
    assert schedule.term == current_term

    # Card 8 requirement: do not skip days
    assert len(schedule.days) == 7

    mon = next(d for d in schedule.days if d.day_of_week == "MON")
    assert [b.course_id for b in mon.blocks] == [course2.id, course.id]  # sorted by start_time


def test_filter_by_current_term(db_session, current_term, student, course):
    # Enrollment in CURRENT_TERM (should appear)
    factories.add_enrollment(db_session, student_id=student.id, course_id=course.id, term=current_term)

    # Enrollment in OTHER_TERM (should NOT appear)
    other_course = factories.make_course(
        db_session,
        semester=OTHER_TERM,
        professor_name="Other Prof",
        day_of_week="TUE",
        start_time=time(10, 0),
        end_time=time(11, 0),
        location="Room 201",
    )

    factories.add_enrollment(db_session, student_id=student.id, course_id=other_course.id, term=OTHER_TERM)

    schedule = build_weekly_schedule(db_session, student_id=student.id)  # uses CURRENT_TERM env

    # Card 8: do not skip days
    assert len(schedule.days) == 7

    all_ids = [b.course_id for day in schedule.days for b in day.blocks]
    assert course.id in all_ids
    assert other_course.id not in all_ids


def test_no_enrollments_returns_all_days_empty(db_session, current_term, student):
    schedule = build_weekly_schedule(db_session, student_id=student.id)

    assert schedule.term == current_term
    assert len(schedule.days) == 7
    assert all(len(day.blocks) == 0 for day in schedule.days)