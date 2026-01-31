# backend/app/services/schedule_service.py

from __future__ import annotations

from typing import Optional, Dict, List

from sqlalchemy.orm import Session

from backend.app.repositories import enrollment_repository, course_repository
from backend.app.schemas.schedule import WeeklyScheduleRead, ScheduleDayRead, ScheduleBlockRead
from backend.app.utils.current_term import get_current_term

DAY_ORDER = ["SAT", "SUN", "MON", "TUE", "WED", "THU", "FRI"]


def build_weekly_schedule(db: Session, student_id: int, term: Optional[str] = None) -> WeeklyScheduleRead:
    effective_term = term or get_current_term()

    enrollments = enrollment_repository.list_student_enrollments(db, student_id, effective_term)

    grouped: Dict[str, List[ScheduleBlockRead]] = {d: [] for d in DAY_ORDER}

    for e in enrollments:
        course = course_repository.get_course_by_id(db, e.course_id)
        if course is None:
            continue

        block = ScheduleBlockRead(
            course_id=course.id,
            code=course.code,
            name=course.name,
            start_time=course.start_time,
            end_time=course.end_time,
            location=course.location,
            professor_name=course.professor_name,
            units=course.units,
        )

        day = course.day_of_week
        if day not in grouped:
            grouped[day] = []
        grouped[day].append(block)

    for day, blocks in grouped.items():
        blocks.sort(key=lambda b: b.start_time)

    days: List[ScheduleDayRead] = [
        ScheduleDayRead(day_of_week=day, blocks=grouped.get(day, [])) for day in DAY_ORDER
    ]

    # If there are unexpected day strings, append them after standard days
    extra_days = sorted([d for d in grouped.keys() if d not in DAY_ORDER])
    for d in extra_days:
        days.append(ScheduleDayRead(day_of_week=d, blocks=grouped[d]))

    return WeeklyScheduleRead(term=effective_term, days=days)