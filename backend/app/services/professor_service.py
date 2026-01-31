# backend/app/services/professor_service.py

from __future__ import annotations

from typing import Optional, List

from sqlalchemy.orm import Session

from backend.app.models.course import Course
from backend.app.models.student import Student
from backend.app.models.enrollment import Enrollment
from backend.app.schemas.professor import ProfessorCourseStudentsRead, ProfessorCourseStudentRead
from backend.app.utils.current_term import get_current_term
from backend.app.repositories import enrollment_repository


class NotCourseOwnerError(Exception):
    pass

class EnrollmentNotFoundError(Exception):
    pass


class NotCurrentTermError(Exception):
    pass

try:
    from backend.app.services.enrollment_service import CourseNotFoundError  # type: ignore
except Exception:  # pragma: no cover
    class CourseNotFoundError(Exception):
        pass


def _normalize_name(value: str | None) -> str:
    return " ".join((value or "").split()).strip().lower()


def _name_sort_key(full_name: str, student_number: str):
    tokens = (full_name or "").split()
    if not tokens:
        last = ""
        first = ""
    else:
        last = tokens[-1].lower()
        first = " ".join(tokens[:-1]).lower()
    return (last, first, str(student_number))


def list_course_students_for_professor(
    db: Session,
    *,
    professor,
    course_id: int,
    term: Optional[str] = None,
) -> ProfessorCourseStudentsRead:
    current = term or get_current_term()

    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise CourseNotFoundError()

    # Ownership check 
    if _normalize_name(course.professor_name) != _normalize_name(getattr(professor, "full_name", None)):
        raise NotCourseOwnerError()

    # Fetch students enrolled in this course in CURRENT term
    # Using explicit join so we don't depend on relationship config.
    rows = (
        db.query(Student)
        .join(Enrollment, Enrollment.student_id == Student.id)
        .filter(Enrollment.course_id == course_id)
        .filter(Enrollment.term == current)
        .all()
    )

    students: List[ProfessorCourseStudentRead] = []
    for s in rows:
        email = getattr(s, "email", None)
        students.append(
            ProfessorCourseStudentRead(
                student_id=s.id,
                student_number=str(getattr(s, "student_number")),
                full_name=getattr(s, "full_name"),
                email=email,
            )
        )

    students.sort(key=lambda x: _name_sort_key(x.full_name, x.student_number))

    return ProfessorCourseStudentsRead(course_id=course_id, term=current, students=students)

def list_professor_courses(
    db: Session,
    *,
    professor,
    term: Optional[str] = None,
) -> List[Course]:
    current_term = term or get_current_term()

    prof_full_name = getattr(professor, "full_name", None)
    prof_norm = _normalize_name(prof_full_name)

    # Scope to current term in DB; ownership match in Python for robust whitespace normalization.
    courses_in_term = db.query(Course).filter(Course.semester == current_term).all()

    owned = [c for c in courses_in_term if _normalize_name(getattr(c, "professor_name", None)) == prof_norm]

    # Stable sort
    if hasattr(Course, "code"):
        owned.sort(key=lambda c: ((c.code or ""), c.id))
    else:
        owned.sort(key=lambda c: c.id)

    return owned



def professor_remove_student(
    db: Session,
    *,
    professor,
    course_id: int,
    student_id: int,
    term: str | None = None,
) -> None:
    """
    Remove a student's enrollment from a course ONLY if it is in the current term.
    Rule #7:
      - enrolled in different term => 409 (NotCurrentTermError)
      - not enrolled at all => 404 (EnrollmentNotFoundError)
    """
    current = term or get_current_term()

    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise CourseNotFoundError()

    if _normalize_name(course.professor_name) != _normalize_name(getattr(professor, "full_name", "")):
        raise NotCourseOwnerError()

    # Try current term first
    enrollment = enrollment_repository.get_by_student_course_term(db, student_id, course_id, current)
    if not enrollment:
        # If enrolled in ANY other term => 409
        any_term = enrollment_repository.get_by_student_course_any_term(db, student_id, course_id)
        if any_term:
            raise NotCurrentTermError()
        raise EnrollmentNotFoundError()

    # Defensive Rule #7 check
    if getattr(enrollment, "term", None) != current:
        raise NotCurrentTermError()

    enrollment_repository.delete(db, enrollment)