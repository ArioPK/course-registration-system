# backend/app/services/drop_service.py

from __future__ import annotations

from typing import Optional
from sqlalchemy.orm import Session

from backend.app.repositories import enrollment_repository, course_repository
from backend.app.services import unit_limit_service
from backend.app.utils.current_term import get_current_term


class NotEnrolledError(Exception):
    pass


class NotCurrentTermError(Exception):
    pass


class UnitMinViolationError(Exception):
    pass


def drop_student_course(
    db: Session,
    *,
    student_id: int,
    course_id: int,
    term: Optional[str] = None,
) -> None:
    """
    Drops a student from a course ONLY for the current term (Rule #6).
    Enforces UnitLimitPolicy.min_units after drop.
    Domain exceptions only.
    """
    current = term or get_current_term()

    # Scope lookup to CURRENT_TERM only
    enrollment = enrollment_repository.get_by_student_course_term(db, student_id, course_id, current)
    if enrollment is None:
        raise NotEnrolledError(
            f"Student is not enrolled in course_id={course_id} for term={current}"
        )

    # Defensive check
    if getattr(enrollment, "term", None) != current:
        raise NotCurrentTermError(
            f"Drop forbidden: enrollment.term={getattr(enrollment, 'term', None)} current_term={current}"
        )

    policy = unit_limit_service.get_unit_limits_service(db)

    current_units = enrollment_repository.sum_student_units(db, student_id, current) or 0

    course = course_repository.get_course_by_id(db, course_id)
    course_units = int(getattr(course, "units", 0) or 0)

    after_units = current_units - course_units
    if after_units < policy.min_units:
        raise UnitMinViolationError(
            f"Min units violation: after_drop={after_units} < min_units={policy.min_units}"
        )

    db.delete(enrollment)
    db.commit()