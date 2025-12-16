from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.dependencies.auth import get_current_student
from backend.app.schemas.course import CourseRead
from backend.app.services.course_service import list_courses_service  # adjust name if needed


router = APIRouter(prefix="/api/student", tags=["student", "courses"])


@router.get("/courses", response_model=List[CourseRead])
def list_offered_courses(
    db: Session = Depends(get_db),
    _current_student=Depends(get_current_student),
) -> List[CourseRead]:
    return list_courses_service(db=db, skip=0, limit=100)
