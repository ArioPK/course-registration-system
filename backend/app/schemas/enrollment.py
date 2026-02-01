# backend/app/schemas/enrollment.py

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from backend.app.schemas.course import CourseRead


class EnrollmentCreate(BaseModel):
    course_id: int = Field(..., ge=1)
    term: Optional[str] = None


class EnrollmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    course_id: int
    term: str
    created_at: Optional[datetime] = None

    # Optional but preferred for UI
    course: Optional[CourseRead] = None