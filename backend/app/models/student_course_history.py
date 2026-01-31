# backend/app/models/student_course_history.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from backend.app.database import Base


class StudentCourseHistory(Base):
    __tablename__ = "student_course_history"

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)

    term = Column(String(32), nullable=False, index=True)

    # Keep it simple: "passed" / "failed"
    status = Column(String(16), nullable=False)

    # Optional grade; choose Float unless your codebase consistently uses Integer
    grade = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("student_id", "course_id", "term", name="uq_history_student_course_term"),
    )

    student = relationship("Student", back_populates="course_history")
    course = relationship("Course", back_populates="course_history")