# backend/app/routers/student_enrollments.py (or wherever your /student/enrollments lives)

from __future__ import annotations

import os
from datetime import datetime, time as dtime
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, Response, status
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.app.database import get_db  

from backend.app.dependencies.auth import get_current_student
from backend.app.models.course import Course
from backend.app.models.enrollment import Enrollment
from backend.app.models.student import Student
from backend.app.services import unit_limit_service

router = APIRouter(prefix="/student", tags=["student"])


def _current_term() -> str:
    return os.getenv("CURRENT_TERM", "1404-1")


class EnrollmentRead(BaseModel):
    course_id: int
    student_id: int
    term: str
    created_at: datetime | None = None


class CourseMiniRead(BaseModel):
    id: int
    code: str
    name: str
    professor_name: str
    day_of_week: str
    start_time: dtime
    end_time: dtime
    location: str
    units: int
    department: str
    semester: str


class StudentEnrollmentItemRead(BaseModel):
    term: str
    created_at: datetime
    course: CourseMiniRead


@router.post("/enrollments", status_code=status.HTTP_201_CREATED, response_model=EnrollmentRead)
def enroll_student(
    payload: dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
    current_student: Student = Depends(get_current_student),
):
    # accept both course_id and courseId
    course_id = payload.get("course_id") or payload.get("courseId")
    if course_id is None:
        raise HTTPException(status_code=422, detail="course_id is required")

    term = payload.get("term") or _current_term()

    course = db.get(Course, int(course_id))
    if not course:
        raise HTTPException(status_code=404, detail="The requested course was not found.")

    # prevent duplicates
    exists = (
        db.query(Enrollment)
        .filter(
            Enrollment.student_id == current_student.id,
            Enrollment.course_id == int(course_id),
            Enrollment.term == term,
        )
        .first()
    )
    if exists:
        raise HTTPException(status_code=409, detail="Student is already enrolled in this course.")

    e = Enrollment(student_id=current_student.id, course_id=int(course_id), term=term)
    db.add(e)
    db.commit()
    db.refresh(e)

    return EnrollmentRead(
        course_id=e.course_id,
        student_id=e.student_id,
        term=e.term,
        created_at=getattr(e, "created_at", None),
    )


@router.get("/enrollments", response_model=list[StudentEnrollmentItemRead])
def list_my_enrollments(
    db: Session = Depends(get_db),
    current_student: Student = Depends(get_current_student),
):
    term = _current_term()

    rows = (
        db.query(Enrollment, Course)
        .join(Course, Course.id == Enrollment.course_id)
        .filter(Enrollment.student_id == current_student.id, Enrollment.term == term)
        .all()
    )

    day_order = {"SAT": 0, "SUN": 1, "MON": 2, "TUE": 3, "WED": 4, "THU": 5, "FRI": 6}

    items: list[StudentEnrollmentItemRead] = []
    for e, c in rows:
        items.append(
            StudentEnrollmentItemRead(
                term=e.term,
                created_at=e.created_at,
                course=CourseMiniRead(
                    id=c.id,
                    code=c.code,
                    name=c.name,
                    professor_name=c.professor_name,
                    day_of_week=c.day_of_week,
                    start_time=c.start_time,
                    end_time=c.end_time,
                    location=c.location,
                    units=c.units,
                    department=c.department,
                    semester=c.semester,
                ),
            )
        )

    items.sort(
        key=lambda it: (
            day_order.get(it.course.day_of_week, 999),
            it.course.start_time,
            it.course.code,
            it.course.id,
        )
    )
    return items


@router.delete("/enrollments/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def drop_student_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_student: Student = Depends(get_current_student),
):
    term = _current_term()

    enrollment = (
        db.query(Enrollment)
        .filter(
            Enrollment.student_id == current_student.id,
            Enrollment.course_id == course_id,
            Enrollment.term == term,
        )
        .first()
    )
    if not enrollment:
        raise HTTPException(status_code=404, detail="Not enrolled in this course")

    course = db.get(Course, course_id)
    if not course:
        # defensive; enrollment references a course that doesn't exist
        raise HTTPException(status_code=404, detail="The requested course was not found.")

    policy = unit_limit_service.get_unit_limits_service(db)
    min_units = int(getattr(policy, "min_units", 0) or 0)

    total_units = (
        db.query(func.coalesce(func.sum(Course.units), 0))
        .select_from(Enrollment)
        .join(Course, Course.id == Enrollment.course_id)
        .filter(Enrollment.student_id == current_student.id, Enrollment.term == term)
        .scalar()
    )
    total_units = int(total_units or 0)

    remaining_units = total_units - int(course.units or 0)
    if remaining_units < min_units:
        raise HTTPException(status_code=409, detail="Dropping would violate minimum units")

    db.delete(enrollment)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)