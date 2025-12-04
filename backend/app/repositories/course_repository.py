# backend/app/repositories/course_repository.py

from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.course import Course
from app.schemas.course import CourseCreate, CourseUpdate


def get_course_by_id(db: Session, course_id: int) -> Optional[Course]:
    """
    Return a single Course by its primary key ID, or None if not found.
    """
    return db.query(Course).filter(Course.id == course_id).first()


def get_courses(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> List[Course]:
    """
    Return a list of courses with basic pagination (offset + limit).
    """
    return (
        db.query(Course)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_course_by_code(db: Session, code: str) -> Optional[Course]:
    """
    Return a single Course by its unique course code, or None if not found.
    Useful for uniqueness checks in the service layer.
    """
    return db.query(Course).filter(Course.code == code).first()


def create_course(db: Session, course_in: CourseCreate) -> Course:
    """
    Create a new Course from a CourseCreate schema and persist it.
    """
    course = Course(**course_in.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


def update_course(
    db: Session,
    db_course: Course,
    course_in: CourseUpdate,
) -> Course:
    """
    Update an existing Course instance in-place using a CourseUpdate schema.

    Only fields that are not None / not unset in course_in are applied
    (PATCH-style behavior).
    """
    # Pydantic v2: model_dump(exclude_unset=True) gives only provided fields
    update_data = course_in.model_dump(exclude_unset=True)

    for field_name, value in update_data.items():
        setattr(db_course, field_name, value)

    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course


def delete_course(db: Session, db_course: Course) -> None:
    """
    Delete an existing Course from the database.
    """
    db.delete(db_course)
    db.commit()
