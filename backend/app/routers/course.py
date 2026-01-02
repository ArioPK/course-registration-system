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
from backend.app.schemas.prerequisite import PrerequisiteCreate, PrerequisiteRead
from backend.app.services.prerequisite_service import (
    add_prerequisite_service,
    list_prerequisites_service,
    remove_prerequisite_service,
    PrerequisiteNotFoundError,
    DuplicatePrerequisiteError,
    InvalidPrerequisiteRelationError,
)
from backend.app.models.admin import Admin
from backend.app.dependencies.auth import get_current_admin, get_current_user_any_role


router = APIRouter(
    prefix="/courses",
    tags=["courses"],
)

@router.get("", response_model=List[CourseRead])
def list_courses(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_any_role),
):
    courses = list_courses_service(db, skip=skip, limit=limit)
    return courses


@router.get("/{course_id}", response_model=CourseRead)
def get_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_any_role),
):
    try:
        course = get_course_service(db, course_id)
        return course
    except CourseNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )


@router.post("", response_model=CourseRead, status_code=status.HTTP_201_CREATED)
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


@router.post(
    "/{course_id}/prerequisites",
    response_model=PrerequisiteRead,
    status_code=status.HTTP_201_CREATED,
)
def add_course_prerequisite(
    course_id: int,
    payload: PrerequisiteCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    # Guard against mismatched body/path (helps avoid accidental wrong linking)
    if payload.course_id != course_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="course_id in path and body must match",
        )

    try:
        link = add_prerequisite_service(db, course_id=course_id, prereq_course_id=payload.prereq_course_id)
        return link
    except InvalidPrerequisiteRelationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except DuplicatePrerequisiteError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except PrerequisiteNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/{course_id}/prerequisites",
    response_model=List[PrerequisiteRead],
)
def list_course_prerequisites(
    course_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    try:
        return list_prerequisites_service(db, course_id=course_id)
    except PrerequisiteNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete(
    "/{course_id}/prerequisites/{prereq_course_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_course_prerequisite(
    course_id: int,
    prereq_course_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    try:
        remove_prerequisite_service(db, course_id=course_id, prereq_course_id=prereq_course_id)
        return None
    except PrerequisiteNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
