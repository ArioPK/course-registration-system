#backend/app/models/__init__.py

from backend.app.models.admin import Admin
from backend.app.models.course import Course
from backend.app.models.student import Student
from backend.app.models.professor import Professor

__all__ = ["Admin", "Course", "Student", "Professor"]