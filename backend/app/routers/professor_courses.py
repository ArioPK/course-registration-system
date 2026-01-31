# backend/app/routers/professor_courses.py

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.dependencies.auth import get_current_professor
from backend.app.schemas.professor import ProfessorCourseStudentsRead
from backend.app.services.professor_service import (
    list_course_students_for_professor,
    NotCourseOwnerError,
    list_professor_courses,
)
from backend.app.services import professor_service


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


@router.delete(
    "/professor/courses/{course_id}/students/{student_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_student_from_course(
    course_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    current_professor=Depends(get_current_professor),
):
    try:
        professor_service.professor_remove_student(
            db,
            professor=current_professor,
            course_id=course_id,
            student_id=student_id,
        )
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except professor_service.NotCourseOwnerError:
        raise HTTPException(status_code=403, detail="Forbidden")
    except professor_service.CourseNotFoundError:
        raise HTTPException(status_code=404, detail="The requested course was not found.")
    except professor_service.EnrollmentNotFoundError:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    except professor_service.NotCurrentTermError:
        raise HTTPException(status_code=409, detail="Cannot remove enrollment outside current term")