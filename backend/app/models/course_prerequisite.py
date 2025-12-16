# backend/app/models/course_prerequisite.py

from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from backend.app.database import Base


class CoursePrerequisite(Base):
    __tablename__ = "course_prerequisites"

    # Composite PK: pair uniquely identifies the association row
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True, index=True)
    prereq_course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True, index=True)

    __table_args__ = (
        UniqueConstraint("course_id", "prereq_course_id", name="uq_course_prereq_pair"),
        CheckConstraint("course_id <> prereq_course_id", name="ck_course_not_self_prereq"),
    )

    # Relationships back to Course (self-referential via two FKs)
    course = relationship("Course", foreign_keys=[course_id], back_populates="prerequisite_links")
    prerequisite = relationship("Course", foreign_keys=[prereq_course_id], back_populates="dependent_links")

    def __repr__(self) -> str:
        return f"<CoursePrerequisite course_id={self.course_id} prereq_course_id={self.prereq_course_id}>"
