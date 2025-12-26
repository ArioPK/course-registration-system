# backend/app/schemas/auth.py

from __future__ import annotations

from typing import Optional, Literal

from pydantic import BaseModel  # type: ignore

try:
    # Pydantic v2
    from pydantic import ConfigDict  # type: ignore
except Exception:  # pragma: no cover
    ConfigDict = None  # type: ignore


class SchemaBase(BaseModel):
    """
    Base schema compatible with Pydantic v1 and v2.

    - v1: orm_mode = True
    - v2: from_attributes = True
    """
    if ConfigDict is not None:
        model_config = ConfigDict(from_attributes=True)
    else:
        class Config:
            orm_mode = True


Role = Literal["admin", "student", "professor"]


class UserContext(SchemaBase):
    role: Role
    identifier: str
    id: Optional[int] = None


class AdminLoginRequest(SchemaBase):
    username: str
    password: str


class StudentLoginRequest(SchemaBase):
    student_number: str
    password: str


class ProfessorLoginRequest(SchemaBase):
    professor_code: str
    password: str


class TokenResponse(SchemaBase):
    access_token: str
    token_type: str
    user: Optional[UserContext] = None
