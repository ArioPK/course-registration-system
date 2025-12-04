# backend/app/schemas/course.py

from __future__ import annotations

from datetime import time
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, conint, constr


class DayOfWeek(str, Enum):
    SATURDAY = "SAT"
    SUNDAY = "SUN"
    MONDAY = "MON"
    TUESDAY = "TUE"
    WEDNESDAY = "WED"
    THURSDAY = "THU"
    FRIDAY = "FRI"


# Shared fields for create / read
class CourseBase(BaseModel):
    code: constr(strip_whitespace=True, min_length=1)
    name: constr(strip_whitespace=True, min_length=1)
    capacity: conint(gt=0)
    professor_name: constr(strip_whitespace=True, min_length=1)
    day_of_week: DayOfWeek
    start_time: time
    end_time: time
    location: constr(strip_whitespace=True, min_length=1)


class CourseCreate(CourseBase):
    """
    Schema for creating a new course.

    All fields are required (except those that might have defaults in CourseBase).
    """
    pass


class CourseUpdate(BaseModel):
    """
    Schema for updating an existing course.

    All fields are optional so this can be used for PATCH-style partial updates.
    Only the provided fields will be updated.
    """
    code: Optional[constr(strip_whitespace=True, min_length=1)] = None
    name: Optional[constr(strip_whitespace=True, min_length=1)] = None
    capacity: Optional[conint(gt=0)] = None
    professor_name: Optional[constr(strip_whitespace=True, min_length=1)] = None
    day_of_week: Optional[DayOfWeek] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    location: Optional[constr(strip_whitespace=True, min_length=1)] = None


class CourseRead(CourseBase):
    """
    Schema returned to clients when reading course data.
    Includes the database ID in addition to CourseBase fields.
    """
    id: int

    # Pydantic v2 config
    model_config = ConfigDict(from_attributes=True)
