# backend/app/schemas/enrollment.py

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from backend.app.schemas.course import CourseRead


class EnrollmentCreate(BaseModel):
    course_id: int = Field(..., ge=1)
    term: Optional[str] = None


class StudentEnrollmentItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    term: str
    created_at: datetime
    course: CourseRead