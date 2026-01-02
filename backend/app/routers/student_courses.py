from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.dependencies.auth import get_current_student
from backend.app.models.student import Student
from backend.app.schemas.course import CourseRead
from backend.app.services.course_service import list_student_catalog_courses_service

router = APIRouter(prefix="/student", tags=["student-courses"])

@router.get("/courses", response_model=List[CourseRead])
def list_student_courses(
    q: Optional[str] = Query(default=None, description="Search across course name and professor name"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    db: Session = Depends(get_db),
    current_student: Student = Depends(get_current_student),
) -> List[CourseRead]:
    return list_student_catalog_courses_service(db, q=q, skip=skip, limit=limit)
