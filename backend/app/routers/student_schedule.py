# backend/app/routers/student_schedule.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.dependencies.auth import get_current_student
from backend.app.models.student import Student
from backend.app.schemas.schedule import WeeklyScheduleRead
from backend.app.services.schedule_service import build_weekly_schedule

router = APIRouter()


@router.get(
    "/student/schedule",
    response_model=WeeklyScheduleRead,
)
def get_weekly_schedule(
    db: Session = Depends(get_db),
    current_student: Student = Depends(get_current_student),
):
    # Service enforces current-term scoping via get_current_term() when term is None
    return build_weekly_schedule(db, student_id=current_student.id)