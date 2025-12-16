# backend/app/services/prerequisite_service.py

from __future__ import annotations

from typing import List
from sqlalchemy.orm import Session

from backend.app.models.course_prerequisite import CoursePrerequisite
from backend.app.repositories import course_repository
from backend.app.repositories import prerequisite_repository


class PrerequisiteNotFoundError(Exception):
    """Raised when a course or prerequisite relation is missing."""


class DuplicatePrerequisiteError(Exception):
    """Raised when trying to create a duplicate prerequisite relation."""


class InvalidPrerequisiteRelationError(Exception):
    """Raised when the prerequisite relation is invalid (e.g., self prerequisite)."""


def list_prerequisites_service(db: Session, course_id: int) -> List[CoursePrerequisite]:
    """
    Return all prerequisite links for a course.
    Business rule: course must exist.
    """
    course = course_repository.get_course_by_id(db, course_id)
    if course is None:
        raise PrerequisiteNotFoundError("Course not found")

    return prerequisite_repository.get_prereqs_for_course(db, course_id)


def add_prerequisite_service(
    db: Session, course_id: int, prereq_course_id: int
) -> CoursePrerequisite:
    """
    Add a prerequisite relation (course_id -> prereq_course_id).

    Rules:
    - no self prerequisite
    - both courses must exist
    - no duplicates
    """
    if course_id == prereq_course_id:
        raise InvalidPrerequisiteRelationError(
            "course_id and prereq_course_id must be different (self-prerequisite is not allowed)."
        )

    course = course_repository.get_course_by_id(db, course_id)
    if course is None:
        raise PrerequisiteNotFoundError("Course not found")

    prereq_course = course_repository.get_course_by_id(db, prereq_course_id)
    if prereq_course is None:
        raise PrerequisiteNotFoundError("Prerequisite course not found")

    # Prefer proactive duplicate check if repo provides it.
    link = getattr(prerequisite_repository, "get_prereq_link", None)
    if callable(link):
        existing = prerequisite_repository.get_prereq_link(db, course_id, prereq_course_id)
        if existing is not None:
            raise DuplicatePrerequisiteError("Prerequisite relation already exists")

    try:
        return prerequisite_repository.add_prereq(db, course_id, prereq_course_id)
    except Exception as exc:
        # If repo raises its own duplicate error, normalize it here:
        if exc.__class__.__name__ == "DuplicatePrerequisiteError":
            raise DuplicatePrerequisiteError("Prerequisite relation already exists") from exc
        raise


def remove_prerequisite_service(db: Session, course_id: int, prereq_course_id: int) -> None:
    """
    Remove a prerequisite relation.

    Rules:
    - relation must exist (otherwise NotFoundError)
    - (optional) validate both courses exist; we validate both to keep logic consistent
    """
    course = course_repository.get_course_by_id(db, course_id)
    if course is None:
        raise PrerequisiteNotFoundError("Course not found")

    prereq_course = course_repository.get_course_by_id(db, prereq_course_id)
    if prereq_course is None:
        raise PrerequisiteNotFoundError("Prerequisite course not found")

    deleted = prerequisite_repository.remove_prereq(db, course_id, prereq_course_id)
    if not deleted:
        raise PrerequisiteNotFoundError("Prerequisite relation not found")
