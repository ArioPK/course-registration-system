# backend/app/models/course.py

from __future__ import annotations

from datetime import datetime, time

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Time # type: ignore
from sqlalchemy.sql import func # type: ignore

from ..database import Base  # relative import from app.database


class Course(Base):
    __tablename__ = "courses"

    id: int = Column(Integer, primary_key=True, index=True)
    code: str = Column(String(20), unique=True, index=True, nullable=False)
    name: str = Column(String(100), nullable=False)
    capacity: int = Column(Integer, nullable=False)
    professor_name: str = Column(String(100), nullable=False)

    # e.g. "SAT", "SUN", "MON", etc.
    day_of_week: str = Column(String(10), nullable=False)

    # Class start/end times
    start_time: time = Column(Time, nullable=False)
    end_time: time = Column(Time, nullable=False)

    # Room / building info
    location: str = Column(String(100), nullable=False)

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

    def __repr__(self) -> str:
        return (
            f"<Course id={self.id!r} "
            f"code={self.code!r} "
            f"name={self.name!r} "
            f"professor_name={self.professor_name!r} "
            f"day_of_week={self.day_of_week!r} "
            f"start_time={self.start_time!r} "
            f"end_time={self.end_time!r}>"
        )
