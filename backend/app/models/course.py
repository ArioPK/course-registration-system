# backend/app/models/course.py

from __future__ import annotations

from datetime import datetime, time

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Time # type: ignore
from sqlalchemy.sql import func # type: ignore

from ..database import Base  # relative import from app.database


class Course(Base):
    __tablename__ = "courses"

    id: int = Column(Integer, primary_key=True, index=True)
    code: str = Column(String(20), index=True, nullable=False)
    name: str = Column(String(100), nullable=False)
    capacity: int = Column(Integer, nullable=False)
    professor_name: str = Column(String(100), nullable=False)

    # e.g. "SAT", "SUN", "MON", etc.
    day_of_week: str = Column(String(10), nullable=False)
    day_of_week2: str = Column(String(10), nullable=True)  # for courses that meet multiple days

    # Class start/end times
    start_time: time = Column(Time, nullable=False)
    start_time2: time = Column(Time, nullable=True)  # for courses that meet multiple times
    end_time: time = Column(Time, nullable=False)
    end_time2: time = Column(Time, nullable=True)  # for courses that meet multiple times

    # Room / building info
    location: str = Column(String(100), nullable=False)
    location2: str = Column(String(100), nullable=True)  # for courses held in multiple locations

    # Optional lifecycle fields
    is_active: bool = Column(Boolean, nullable=False, default=True)

    created_at: datetime = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: datetime = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    
    units: int = Column(Integer, nullable=False)                   # 1..4 units
    major: str = Column(String(100), nullable=False)               # e.g. “Computer Engineering”
    semester: str = Column(String(20), nullable=False)             # e.g. “2025-1”
    prerequisites: str = Column(String(200), nullable=True)        # comma‑separated course codes/IDs


    def __repr__(self) -> str:
        return (
            f"<Course id={self.id!r} "
            f"code={self.code!r} "
            f"name={self.name!r} "
            f"professor_name={self.professor_name!r} "
            f"day_of_week={self.day_of_week!r} "
            f"day_of_week2={self.day_of_week2!r} "
            f"start_time={self.start_time!r} "
            f"start_time2={self.start_time2!r} "
            f"end_time={self.end_time!r}"
            f"end_time2={self.end_time2!r}"
            f"location={self.location!r}"
            f"location2={self.location2!r}"
            f"units={self.units!r}"
            f"major={self.major!r}"
            f"semester={self.semester!r}"
            f"prerequisites={self.prerequisites!r}>"
        )
