# backend/app/repositories/enrollment_repository.py

from __future__ import annotations

from typing import Optional, List

from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.models.enrollment import Enrollment
from backend.app.models.course import Course


def create(db: Session, *, student_id: int, course_id: int, term: str) -> Enrollment:
    enrollment = Enrollment(student_id=student_id, course_id=course_id, term=term)
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment


def delete(db: Session, enrollment: Enrollment) -> None:
    db.delete(enrollment)
    db.commit()


def get_by_student_course_term(
    db: Session, student_id: int, course_id: int, term: str
) -> Optional[Enrollment]:
    return (
        db.query(Enrollment)
        .filter(
            Enrollment.student_id == student_id,
            Enrollment.course_id == course_id,
            Enrollment.term == term,
        )
        .first()
    )


def count_course_enrollments(db: Session, course_id: int, term: str) -> int:
    return (
        db.query(func.count(Enrollment.id))
        .filter(Enrollment.course_id == course_id, Enrollment.term == term)
        .scalar()
        or 0
    )


def list_student_enrollments(db: Session, student_id: int, term: str) -> List[Enrollment]:
    return (
        db.query(Enrollment)
        .filter(Enrollment.student_id == student_id, Enrollment.term == term)
        .order_by(Enrollment.id.asc())
        .all()
    )


def sum_student_units(db: Session, student_id: int, term: str) -> int:
    total = (
        db.query(func.coalesce(func.sum(Course.units), 0))
        .select_from(Enrollment)
        .join(Course, Course.id == Enrollment.course_id)
        .filter(Enrollment.student_id == student_id, Enrollment.term == term)
        .scalar()
    )
    return int(total or 0)


def list_course_enrollments(db: Session, course_id: int, term: str) -> List[Enrollment]:
    return (
        db.query(Enrollment)
        .filter(Enrollment.course_id == course_id, Enrollment.term == term)
        .order_by(Enrollment.id.asc())
        .all()
    )


def get_by_student_course_any_term(db: Session, student_id: int, course_id: int) -> Enrollment | None:
    """
    Returns an enrollment for (student_id, course_id) regardless of term.
    Used to distinguish "not enrolled" vs "enrolled but not in current term".
    """
    return (
        db.query(Enrollment)
        .filter(Enrollment.student_id == student_id, Enrollment.course_id == course_id)
        .first()
    )