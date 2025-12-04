# backend/app/services/course_service.py

from __future__ import annotations

from typing import List

from sqlalchemy.orm import Session

from app.models.course import Course
from app.schemas.course import CourseCreate, CourseUpdate
from app.repositories.course_repository import (
    get_course_by_id,
    get_courses,
    get_course_by_code,
    create_course,
    update_course,
    delete_course,
)


class CourseNotFoundError(Exception):
    """Raised when a course with the given ID does not exist."""


class DuplicateCourseCodeError(Exception):
    """Raised when trying to create or update a course with a duplicate code."""


def list_courses_service(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> List[Course]:
    """
    Return a paginated list of courses.
    This is a thin wrapper over the repository to keep the service API consistent.
    """
    return get_courses(db=db, skip=skip, limit=limit)


def get_course_service(db: Session, course_id: int) -> Course:
    """
    Return a single course by ID.

    Raises:
        CourseNotFoundError: if no course with the given ID exists.
    """
    course = get_course_by_id(db=db, course_id=course_id)
    if course is None:
        raise CourseNotFoundError(f"Course with id={course_id} not found")
    return course


def create_course_service(db: Session, course_in: CourseCreate) -> Course:
    """
    Create a new course after enforcing basic business rules.

    - Course code must be unique.
    """
    existing = get_course_by_code(db=db, code=course_in.code)
    if existing is not None:
        raise DuplicateCourseCodeError(
            f"Course with code '{course_in.code}' already exists"
        )

    course = create_course(db=db, course_in=course_in)
    return course


def update_course_service(
    db: Session,
    course_id: int,
    course_in: CourseUpdate,
) -> Course:
    """
    Update an existing course.

    Steps:
    - Ensure course exists.
    - If the code is being changed, ensure the new code is still unique.
    - Apply partial updates via repository.
    """
    db_course = get_course_by_id(db=db, course_id=course_id)
    if db_course is None:
        raise CourseNotFoundError(f"Course with id={course_id} not found")

    # Check for code uniqueness if a new code is provided
    if course_in.code is not None:
        if course_in.code != db_course.code:
            existing = get_course_by_code(db=db, code=course_in.code)
            if existing is not None and existing.id != db_course.id:
                raise DuplicateCourseCodeError(
                    f"Course with code '{course_in.code}' already exists"
                )

    updated_course = update_course(db=db, db_course=db_course, course_in=course_in)
    return updated_course


def delete_course_service(db: Session, course_id: int) -> None:
    """
    Delete a course by its ID.

    Raises:
        CourseNotFoundError: if the course does not exist.
    """
    db_course = get_course_by_id(db=db, course_id=course_id)
    if db_course is None:
        raise CourseNotFoundError(f"Course with id={course_id} not found")

    delete_course(db=db, db_course=db_course)
