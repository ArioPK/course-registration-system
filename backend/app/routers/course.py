# backend/app/routers/course.py


from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.schemas.course import CourseCreate, CourseUpdate, CourseRead
from backend.app.services.course_service import (
    create_course_service,
    list_courses_service,
    get_course_service,
    update_course_service,
    delete_course_service,
    CourseNotFoundError,
    DuplicateCourseCodeError,
)
from backend.app.models.admin import Admin
from backend.app.dependencies.auth import get_current_admin


router = APIRouter(
    prefix="/courses",
    tags=["courses"],
)

@router.get("/", response_model=List[CourseRead])
def list_courses(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    courses = list_courses_service(db, skip=skip, limit=limit)
    return courses


@router.get("/{course_id}", response_model=CourseRead)
def get_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    try:
        course = get_course_service(db, course_id)
        return course
    except CourseNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )


@router.post("/", response_model=CourseRead, status_code=status.HTTP_201_CREATED)
def create_course(
    course_in: CourseCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    try:
        course = create_course_service(db, course_in)
        return course
    except DuplicateCourseCodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course with this code already exists",
        )


@router.put("/{course_id}", response_model=CourseRead)
def update_course(
    course_id: int,
    course_in: CourseUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    try:
        course = update_course_service(db, course_id, course_in)
        return course
    except CourseNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )
    except DuplicateCourseCodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course with this code already exists",
        )


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
    
):
    try:
        delete_course_service(db, course_id)
    except CourseNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

