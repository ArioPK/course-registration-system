from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from backend.app.repositories import enrollment_repository
from backend.app.schemas.course import CourseRead
from backend.app.schemas.enrollment import StudentEnrollmentItemRead
from backend.app.utils.current_term import get_current_term

# UI-friendly stable order
_DAY_ORDER = ["SAT", "SUN", "MON", "TUE", "WED", "THU", "FRI"]
_DAY_RANK = {d: i for i, d in enumerate(_DAY_ORDER)}


def list_my_enrollments(
    db: Session,
    *,
    student_id: int,
    term: Optional[str] = None,
) -> list[StudentEnrollmentItemRead]:
    current = term or get_current_term()

    enrollments = enrollment_repository.list_student_enrollments(
        db, student_id=student_id, term=current
    )

    items: list[StudentEnrollmentItemRead] = []
    for e in enrollments:
        # Be defensive about naming differences (term vs semester) across codebases
        e_term = getattr(e, "term", None) or getattr(e, "semester", None) or current

        # Expect enrollment->course relationship; if your repo returns rows w/ course already joined, this still works.
        course_obj = getattr(e, "course", None)
        if course_obj is None:
            # If your repository returns course separately, adapt here.
            # But per your assumptions, relationship/join exists.
            raise RuntimeError("Enrollment.course not loaded; ensure repo joins course relationship.")

        course_read = CourseRead.model_validate(course_obj)

        items.append(
            StudentEnrollmentItemRead(
                term=e_term,
                created_at=e.created_at,
                course=course_read,
            )
        )

    def _sort_key(item: StudentEnrollmentItemRead):
        c = item.course
        day = getattr(c, "day_of_week", None) or getattr(c, "dayOfWeek", None)
        start = getattr(c, "start_time", None) or getattr(c, "startTime", None)
        code = getattr(c, "code", "") or ""
        cid = getattr(c, "id", 0) or 0

        day_rank = _DAY_RANK.get(str(day).upper(), 999) if day is not None else 999
        return (day_rank, start or "", code, cid)

    return sorted(items, key=_sort_key)