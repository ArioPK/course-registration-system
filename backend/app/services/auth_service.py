# backend/app/services/auth_service.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

from sqlalchemy.orm import Session  # type: ignore

from backend.app.models.admin import Admin
from backend.app.models.student import Student
from backend.app.models.professor import Professor
from backend.app.services.security import verify_password

Role = Literal["admin", "student", "professor"]


@dataclass(frozen=True)
class AuthResult:
    role: Role
    identifier: str
    id: Optional[int] = None


class InvalidCredentialsError(Exception):
    """Raised for unknown identifier OR wrong password (generic, no user enumeration)."""


class InactiveAccountError(Exception):
    """Raised when a matching account exists but is inactive."""
    def __init__(self, role: Role):
        self.role = role
        super().__init__(f"Inactive {role} account")


def authenticate_any_role(db: Session, username: str, password: str) -> AuthResult:
    """
    Unified login authentication (backend-only shim).

    Precedence (important for collisions):
      1) Admin.username
      2) Student.student_number
      3) Professor.professor_code

    Collision behavior:
      - If an Admin with the identifier exists, we DO NOT fall through to student/professor.
        A password mismatch returns InvalidCredentialsError immediately.
    """

    # 1) Admin
    admin = db.query(Admin).filter(Admin.username == username).first()
    if admin is not None:
        if not verify_password(password, admin.password_hash):
            raise InvalidCredentialsError()
        # Keep admin behavior unchanged (do not block inactive admin here unless you already do elsewhere)
        return AuthResult(role="admin", identifier=admin.username, id=getattr(admin, "id", None))

    # 2) Student
    student = db.query(Student).filter(Student.student_number == username).first()
    if student is not None:
        if hasattr(student, "is_active") and not student.is_active:
            raise InactiveAccountError("student")
        if not verify_password(password, student.password_hash):
            raise InvalidCredentialsError()
        return AuthResult(role="student", identifier=student.student_number, id=getattr(student, "id", None))

    # 3) Professor
    professor = db.query(Professor).filter(Professor.professor_code == username).first()
    if professor is not None:
        if hasattr(professor, "is_active") and not professor.is_active:
            raise InactiveAccountError("professor")
        if not verify_password(password, professor.password_hash):
            raise InvalidCredentialsError()
        return AuthResult(role="professor", identifier=professor.professor_code, id=getattr(professor, "id", None))

    # Unknown identifier
    raise InvalidCredentialsError()
