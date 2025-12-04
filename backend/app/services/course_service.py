# backend/app/services/course_service.py

from sqlalchemy.orm import Session

from app.models.course import Course
from app.schemas.course import CourseCreate, CourseUpdate
from app.repositories.course_repository import (
    get_course_by_id,
    get_course_by_code,
    get_courses,
    create_course,
    update_course,
    delete_course,
)


def create_course_service(db: Session, course_in: CourseCreate) -> Course:
    # Example of enforcing uniqueness (service layer concern)
    existing = get_course_by_code(db, course_in.code)
    if existing:
        # later: raise a domain-specific exception, then translate to HTTP in the router
        raise ValueError("Course with this code already exists")
    return create_course(db, course_in)
