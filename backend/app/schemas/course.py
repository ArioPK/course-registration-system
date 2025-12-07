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

class Major(str, Enum):
    COMPUTER_ENGINEERING = "Computer Engineering"
    MECHANICAL_ENGINEERING = "Mechanical Engineering"
    CIVIL_ENGINEERING = "Civil Engineering"
    ELECTRICAL_ENGINEERING = "Electrical Engineering"
    SOFTWARE_ENGINEERING = "Software Engineering"
    COMPUTER_SCIENCE = "Computer Science"
    INFORMATION_TECHNOLOGY = "Information Technology"
    BIOENGINEERING = "Bioengineering"
    AEROSPACE_ENGINEERING = "Aerospace Engineering"
    CHEMICAL_ENGINEERING = "Chemical Engineering"
    ENVIRONMENTAL_ENGINEERING = "Environmental Engineering"
    INDUSTRIAL_ENGINEERING = "Industrial Engineering"
    MATERIALS_SCIENCE = "Materials Science"
    DATA_SCIENCE = "Data Science"
    ARTIFICIAL_INTELLIGENCE = "Artificial Intelligence"
    NETWORK_ENGINEERING = "Network Engineering"
    ELECTRONICS_ENGINEERING = "Electronics Engineering"
    TELECOMMUNICATIONS_ENGINEERING = "Telecommunications Engineering"
    MEDICAL_ENGINEERING = "Medical Engineering"
    BIOMEDICAL_ENGINEERING = "Biomedical Engineering"
    NUCLEAR_ENGINEERING = "Nuclear Engineering"
    MECHATRONICS_ENGINEERING = "Mechatronics Engineering"
    ROBOTICS_ENGINEERING = "Robotics Engineering"
    AGRICULTURAL_ENGINEERING = "Agricultural Engineering"
    MARINE_ENGINEERING = "Marine Engineering"
    ARCHITECTURE = "Architecture"
    URBAN_PLANNING = "Urban Planning"
    PSYCHOLOGY = "Psychology"
    ECONOMICS = "Economics"
    BUSINESS_ADMINISTRATION = "Business Administration"
    ACCOUNTING = "Accounting"
    MANAGEMENT = "Management"
    MARKETING = "Marketing"
    FINANCE = "Finance"
    LAW = "Law"
    MEDICINE = "Medicine"
    DENTISTRY = "Dentistry"
    PHARMACY = "Pharmacy"
    VETERINARY_MEDICINE = "Veterinary Medicine"
    EDUCATION = "Education"
    PHYSICS = "Physics"
    MATHEMATICS = "Mathematics"
    CHEMISTRY = "Chemistry"
    BIOLOGY = "Biology"
    AGRICULTURAL_SCIENCES = "Agricultural Sciences"
    LINGUISTICS = "Linguistics"
    PHILOSOPHY = "Philosophy"
    HISTORY = "History"
    POLITICAL_SCIENCE = "Political Science"
    SOCIOLOGY = "Sociology"
    ANTHROPOLOGY = "Anthropology"

# Shared fields for create / read
class CourseBase(BaseModel):
    code: constr(strip_whitespace=True, min_length=1)
    name: constr(strip_whitespace=True, min_length=2)
    capacity: conint(gt=0)
    professor_name: constr(strip_whitespace=True, min_length=1)
    day_of_week: DayOfWeek
    day_of_week2: Optional[DayOfWeek] = None          # for courses that meet multiple days
    start_time: time
    start_time2: Optional[time] = None                # for courses that meet multiple times
    end_time: time
    end_time2: Optional[time] = None                  # for courses that meet multiple times
    location: constr(strip_whitespace=True, min_length=1)
    location2: Optional[constr(strip_whitespace=True, min_length=1)] = None  # for courses held in multiple locations
    units: conint(ge=1, le=4)                                   # must be 1–4
    major: Major                                                # restrict to valid majors
    semester: constr(strip_whitespace=True, min_length=1)       # e.g. “2025-1”
    prerequisites: Optional[List[int]] = None                   # list of course IDs

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
    day_of_week2: Optional[DayOfWeek] = None
    start_time: Optional[time] = None
    start_time2: Optional[time] = None
    end_time: Optional[time] = None
    end_time2: Optional[time] = None
    location: Optional[constr(strip_whitespace=True, min_length=1)] = None
    location2: Optional[constr(strip_whitespace=True, min_length=1)] = None
    units: Optional[conint(ge=1, le=4)] = None
    major: Optional[Major] = None
    semester: Optional[constr(strip_whitespace=True, min_length=1)] = None
    prerequisites: Optional[List[int]] = None


class CourseRead(CourseBase):
    """
    Schema returned to clients when reading course data.
    Includes the database ID in addition to CourseBase fields.
    """
    id: int

    # Pydantic v2 config
    model_config = ConfigDict(from_attributes=True)
