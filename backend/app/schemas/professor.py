# backend/app/schemas/professor.py

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class ProfessorCourseStudentRead(BaseModel):
    student_id: int
    student_number: str
    full_name: str
    email: Optional[str] = None


class ProfessorCourseStudentsRead(BaseModel):
    course_id: int
    term: str
    students: list[ProfessorCourseStudentRead]