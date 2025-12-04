# backend/app/routers/course.py

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.course import CourseCreate, CourseRead, CourseUpdate
from app.services.course_service import (
    create_course_service,
    list_courses_service,
    get_course_service,
    update_course_service,
    delete_course_service,
    CourseNotFoundError,
    DuplicateCourseCodeError,
)

router = APIRouter(prefix="/courses", tags=["courses"])


@router.post("/", response_model=CourseRead, status_code=status.HTTP_201_CREATED)
def create_course_endpoint(
    course_in: CourseCreate,
    db: Session = Depends(get_db),
):
    try:
        course = create_course_service(db=db, course_in=course_in)
        return course
    except DuplicateCourseCodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get("/", response_model=List[CourseRead])
def list_courses_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    courses = list_courses_service(db=db, skip=skip, limit=limit)
    return courses
