# backend/app/repositories/course_history_repository.py

from __future__ import annotations

from typing import Optional, List

from sqlalchemy.orm import Session

from backend.app.models.student_course_history import StudentCourseHistory


def has_passed_course(db: Session, student_id: int, course_id: int) -> bool:
    """
    Returns True if the student has ANY history record for the course with status == "passed".
    """
    row = (
        db.query(StudentCourseHistory.id)
        .filter(
            StudentCourseHistory.student_id == student_id,
            StudentCourseHistory.course_id == course_id,
            StudentCourseHistory.status == "passed",
        )
        .first()
    )
    return row is not None


def list_passed_courses(db: Session, student_id: int) -> List[int]:
    """
    Returns a distinct list of course_id values for which the student has status == "passed".
    Stable ordering: course_id ASC.
    """
    rows = (
        db.query(StudentCourseHistory.course_id)
        .filter(
            StudentCourseHistory.student_id == student_id,
            StudentCourseHistory.status == "passed",
        )
        .distinct()
        .order_by(StudentCourseHistory.course_id.asc())
        .all()
    )
    return [course_id for (course_id,) in rows]


def create_history_record(
    db: Session,
    *,
    student_id: int,
    course_id: int,
    term: str,
    status: str,
    grade: Optional[float] = None,
) -> StudentCourseHistory:
    """
    Convenience helper for tests/demo. Keeps logic minimal.
    """
    record = StudentCourseHistory(
        student_id=student_id,
        course_id=course_id,
        term=term,
        status=status,
        grade=grade,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record