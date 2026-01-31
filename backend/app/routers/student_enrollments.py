# backend/app/routers/student_enrollments.py

from fastapi import APIRouter, Depends, HTTPException, Response, status
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

# Drop service import (Card 6). Supports either module location:
try:
    from backend.app.services import drop_service as _drop_mod
except ImportError:  # pragma: no cover
    from backend.app.services import enrollment_service as _drop_mod  # type: ignore

drop_student_course = _drop_mod.drop_student_course
NotEnrolledError = getattr(_drop_mod, "NotEnrolledError")
NotCurrentTermError = getattr(_drop_mod, "NotCurrentTermError", ())
UnitMinViolationError = (
    getattr(_drop_mod, "UnitMinViolationError", None)
    or getattr(_drop_mod, "UnitLimitViolationError", ())
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


@router.delete(
    "/student/enrollments/{course_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def drop_course_enrollment(
    course_id: int,
    db: Session = Depends(get_db),
    current_student: Student = Depends(get_current_student),
):
    try:
        drop_student_course(db, student_id=current_student.id, course_id=course_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except NotEnrolledError:
        raise HTTPException(status_code=404, detail="Not enrolled in this course")
    except NotCurrentTermError:
        raise HTTPException(status_code=409, detail="Cannot drop outside current term")
    except UnitMinViolationError:
        raise HTTPException(status_code=409, detail="Dropping would violate minimum units")