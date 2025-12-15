# backend/app/models/student.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from sqlalchemy.sql import func

from backend.app.database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Login identifier
    student_number = Column(String(32), unique=True, index=True, nullable=False)

    # Profile fields
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=True)

    # Identity / academic info
    national_id = Column(String(32), unique=True, index=True, nullable=False)
    phone_number = Column(String(32), nullable=True)
    major = Column(String(128), nullable=True)
    entry_year = Column(Integer, nullable=True)

    # Academic progress (can evolve later)
    units_taken = Column(Integer, nullable=False, default=0)
    mark = Column(Float, nullable=True)

    # Auth
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Student id={self.id} student_number={self.student_number!r} full_name={self.full_name!r}>"
