# backend/app/services/enrollment_service.py

from __future__ import annotations

from typing import Optional, Iterable

from sqlalchemy.orm import Session

from backend.app.models.course import Course
from backend.app.models.enrollment import Enrollment

from backend.app.repositories import (
    enrollment_repository,
    prerequisite_repository,
    course_history_repository,
    course_repository,
)

from backend.app.services import unit_limit_service


class PrereqNotMetError(Exception):
    pass


class TimeConflictError(Exception):
    pass


class CapacityFullError(Exception):
    pass


class DuplicateEnrollmentError(Exception):
    pass


class UnitLimitViolationError(Exception):
    pass


class CourseNotFoundError(Exception):
    pass


def _overlaps(a_start, a_end, b_start, b_end) -> bool:
    # If end == start => NOT a conflict (back-to-back allowed)
    return (a_start < b_end) and (b_start < a_end)


def enroll_student(
    db: Session,
    *,
    student_id: int,
    course_id: int,
    term: Optional[str] = None,
) -> Enrollment:
    # a) Load Course
    course = course_repository.get_course_by_id(db, course_id)
    if course is None:
        raise CourseNotFoundError(f"Course not found: course_id={course_id}")

    # b) Determine term
    effective_term = term or course.semester

    # c) Duplicate enrollment check
    if enrollment_repository.get_by_student_course_term(db, student_id, course_id, effective_term):
        raise DuplicateEnrollmentError(
            f"Duplicate enrollment: student_id={student_id}, course_id={course_id}, term={effective_term}"
        )

    # d) Capacity check
    cnt = enrollment_repository.count_course_enrollments(db, course_id, effective_term)
    if cnt >= course.capacity:
        raise CapacityFullError(f"Course is full: course_id={course_id}, term={effective_term}")

    # e) Prereqs check
    prereqs = prerequisite_repository.get_prereqs_for_course(db, course_id)
    missing = []
    for link in prereqs:
        # Adjust attribute name based on your model (common ones shown below)
        prereq_course_id = getattr(link, "prerequisite_course_id", None) or getattr(link, "prereq_course_id", None)
        if prereq_course_id is None:
            # Fallback: some codebases name it "course_id" for the prereq link side
            prereq_course_id = getattr(link, "course_id", None)

        if prereq_course_id is None:
            continue

        if not course_history_repository.has_passed_course(db, student_id, prereq_course_id):
            missing.append(prereq_course_id)

    if missing:
        raise PrereqNotMetError(f"Missing passed prerequisites for course_id={course_id}: {missing}")

    # f) Time conflict check
    existing = enrollment_repository.list_student_enrollments(db, student_id, effective_term)
    for e in existing:
        existing_course = course_repository.get_course_by_id(db, e.course_id)
        if existing_course is None:
            continue

        if course.day_of_week == existing_course.day_of_week and _overlaps(
            course.start_time, course.end_time,
            existing_course.start_time, existing_course.end_time
        ):
            raise TimeConflictError(
                f"Time conflict with course_id={existing_course.id} for student_id={student_id} in term={effective_term}"
            )

    # g) Unit limit check
    policy = unit_limit_service.get_unit_limits_service(db)
    current_units = enrollment_repository.sum_student_units(db, student_id, effective_term)
    if current_units + course.units > policy.max_units:
        raise UnitLimitViolationError(
            f"Unit limit exceeded: current={current_units}, new={course.units}, max={policy.max_units}"
        )

    # h) Create enrollment (let IntegrityError bubble)
    return enrollment_repository.create(db, student_id=student_id, course_id=course_id, term=effective_term)