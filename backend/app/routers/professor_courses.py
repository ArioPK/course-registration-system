# backend/app/routers/professor_courses.py

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.dependencies.auth import get_current_professor
from backend.app.schemas.professor import ProfessorCourseStudentsRead
from backend.app.services.professor_service import (
    list_course_students_for_professor,
    NotCourseOwnerError,
    list_professor_courses,
)

# Prefer the existing CourseRead schema. Provide a minimal fallback if not present.
try:
    from backend.app.schemas.course import CourseRead
except Exception:  # pragma: no cover
    from pydantic import BaseModel
    from datetime import time


try:
    from backend.app.services.enrollment_service import CourseNotFoundError  # type: ignore
except Exception:  # pragma: no cover
    class CourseNotFoundError(Exception):
        pass


    class CourseRead(BaseModel):
        id: int
        code: str
        name: str
        professor_name: str
        day_of_week: str
        start_time: time
        end_time: time
        location: str
        units: int
        department: str
        semester: str

        class Config:
            from_attributes = True


router = APIRouter()


@router.get(
    "/professor/courses",
    response_model=list[CourseRead],
)
def get_professor_courses(
    db: Session = Depends(get_db),
    current_professor=Depends(get_current_professor),
):
    return list_professor_courses(db, professor=current_professor)


@router.get(
    "/professor/courses/{course_id}/students",
    response_model=ProfessorCourseStudentsRead,
)
def get_course_students_for_professor(
    course_id: int,
    db: Session = Depends(get_db),
    current_professor=Depends(get_current_professor),
):
    try:
        return list_course_students_for_professor(
            db,
            professor=current_professor,
            course_id=course_id,
        )
    except NotCourseOwnerError:
        raise HTTPException(status_code=403, detail="You do not have access to this course.")
    except CourseNotFoundError:
        raise HTTPException(status_code=404, detail="The requested course was not found.")