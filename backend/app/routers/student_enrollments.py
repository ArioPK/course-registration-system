# backend/app/routers/student_enrollments.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.student import Student
from backend.app.schemas.enrollment import EnrollmentCreate, EnrollmentRead
from backend.app.dependencies.auth import get_current_student
from backend.app.services.enrollment_service import (
    enroll_student,
    PrereqNotMetError,
    TimeConflictError,
    CapacityFullError,
    DuplicateEnrollmentError,
    UnitLimitViolationError,
    CourseNotFoundError,
)

router = APIRouter()


@router.post(
    "/student/enrollments",
    response_model=EnrollmentRead,
    status_code=status.HTTP_201_CREATED,
)
def enroll_in_course(
    enrollment: EnrollmentCreate,
    db: Session = Depends(get_db),
    current_student: Student = Depends(get_current_student),
):
    try:
        return enroll_student(
            db,
            student_id=current_student.id,
            course_id=enrollment.course_id,
            term=enrollment.term,
        )
    except PrereqNotMetError:
        raise HTTPException(status_code=400, detail="Prerequisites not met for this course.")
    except TimeConflictError:
        raise HTTPException(status_code=409, detail="There is a time conflict with another enrolled course.")
    except CapacityFullError:
        raise HTTPException(status_code=409, detail="This course is at full capacity.")
    except DuplicateEnrollmentError:
        raise HTTPException(status_code=409, detail="You are already enrolled in this course.")
    except UnitLimitViolationError:
        raise HTTPException(status_code=400, detail="You have exceeded the maximum allowed units for this term.")
    except CourseNotFoundError:
        raise HTTPException(status_code=404, detail="The requested course was not found.")