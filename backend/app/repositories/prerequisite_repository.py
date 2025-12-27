# backend/app/repositories/prerequisite_repository.py

from typing import List, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.models.course_prerequisite import CoursePrerequisite


class DuplicatePrerequisiteError(Exception):
    """Raised when attempting to add a duplicate prerequisite relation."""
    pass


def get_prereq_link(
    db: Session, course_id: int, prereq_course_id: int
) -> Optional[CoursePrerequisite]:
    """Return the prerequisite link row if it exists, otherwise None."""
    return (
        db.query(CoursePrerequisite)
        .filter(
            CoursePrerequisite.course_id == course_id,
            CoursePrerequisite.prereq_course_id == prereq_course_id,
        )
        .first()
    )


def get_prereqs_for_course(db: Session, course_id: int) -> List[CoursePrerequisite]:
    """Return all prerequisite links for a given course_id."""
    return (
        db.query(CoursePrerequisite)
        .filter(CoursePrerequisite.course_id == course_id)
        .all()
    )


def get_all_prereqs(db: Session) -> List[CoursePrerequisite]:
    """Return all prerequisite links across all courses (stable ordering)."""
    return (
        db.query(CoursePrerequisite)
        .order_by(CoursePrerequisite.course_id.asc(), CoursePrerequisite.prereq_course_id.asc())
        .all()
    )


def get_all_prereqs(db: Session) -> List[CoursePrerequisite]:
    """Return all prerequisite links across all courses (stable ordering)."""
    return (
        db.query(CoursePrerequisite)
        .order_by(
            CoursePrerequisite.course_id.asc(),
            CoursePrerequisite.prereq_course_id.asc(),
        )
        .all()
    )


def add_prereq(db: Session, course_id: int, prereq_course_id: int) -> CoursePrerequisite:
    """
    Create a course -> prerequisite relationship.

    Raises:
        ValueError: if course_id == prereq_course_id (self prerequisite).
        DuplicatePrerequisiteError: if the relationship already exists.
    """
    if course_id == prereq_course_id:
        raise ValueError("course_id and prereq_course_id must be different (self-prerequisite is not allowed).")

    # Pre-check to provide a clean error (still keep IntegrityError handling for race-safety)
    existing = get_prereq_link(db, course_id, prereq_course_id)
    if existing is not None:
        raise DuplicatePrerequisiteError("Prerequisite relation already exists.")

    link = CoursePrerequisite(course_id=course_id, prereq_course_id=prereq_course_id)
    db.add(link)

    try:
        db.commit()
        # Works whether PK is composite or surrogate; we do not assume `id` exists.
        db.refresh(link)
    except IntegrityError as exc:
        db.rollback()
        # Unique constraint collision or FK issues (FK issues should be handled in service later)
        raise DuplicatePrerequisiteError("Prerequisite relation already exists.") from exc

    return link


def remove_prereq(db: Session, course_id: int, prereq_course_id: int) -> bool:
    """
    Remove a course -> prerequisite relationship.

    Returns:
        True if deleted, False if not found.
    """
    link = get_prereq_link(db, course_id, prereq_course_id)
    if link is None:
        return False

    db.delete(link)
    db.commit()
    return True