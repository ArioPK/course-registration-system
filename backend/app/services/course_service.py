# backend/app/services/course_service.py

from __future__ import annotations

from typing import Optional,List

from sqlalchemy.orm import Session

from backend.app.models.course import Course
from backend.app.repositories.course_repository import list_courses_filtered
from backend.app.schemas.course import CourseCreate, CourseUpdate
from backend.app.repositories.course_repository import (
    get_course_by_id,
    get_courses,
    get_course_by_code,
    create_course,
    update_course,
    delete_course,
)
from backend.app.repositories import enrollment_repository

def list_student_catalog_courses_service(
    db: Session,
    *,
    q: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Course]:
    # normalize empty/whitespace queries to None
    if q is not None and not q.strip():
        q = None

    return list_courses_filtered(db, q=q, skip=skip, limit=limit, only_active=True)

class CourseNotFoundError(Exception):
    """Raised when a course with the given ID does not exist."""


class DuplicateCourseCodeError(Exception):
    """Raised when trying to create or update a course with a duplicate code."""


def list_courses_service(db: Session, skip: int = 0, limit: int = 100) -> List[Course]:
    courses = get_courses(db=db, skip=skip, limit=limit)

    for c in courses:
        c.enrolled = enrollment_repository.count_course_enrollments(db, c.id, c.semester)

    return courses


def get_course_service(db: Session, course_id: int) -> Course:
    course = get_course_by_id(db=db, course_id=course_id)
    if course is None:
        raise CourseNotFoundError(f"Course with id={course_id} not found")

    course.enrolled = enrollment_repository.count_course_enrollments(db, course.id, course.semester)

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
