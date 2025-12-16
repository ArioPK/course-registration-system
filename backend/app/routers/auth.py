# backend/app/routers/auth.py

from __future__ import annotations

from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status # type: ignore
from sqlalchemy.orm import Session # type: ignore

from backend.app.config.settings import settings
from backend.app.database import get_db
from backend.app.models.admin import Admin
from backend.app.schemas.auth import AdminLoginRequest, TokenResponse # type: ignore
from backend.app.models.student import Student
from backend.app.schemas.auth import StudentLoginRequest, TokenResponse
from backend.app.models.professor import Professor
from backend.app.schemas.auth import ProfessorLoginRequest, TokenResponse
from backend.app.services.security import verify_password
from backend.app.services.jwt import create_access_token

# to test rout
from ..dependencies.auth import get_current_admin
from ..models.admin import Admin


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post("/professor/login", response_model=TokenResponse)
async def professor_login(
    credentials: ProfessorLoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect code or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

    professor = (
        db.query(Professor)
        .filter(Professor.professor_code == credentials.professor_code)
        .first()
    )
    if not professor:
        raise credentials_exception

    if not professor.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive professor account",
        )

    if not verify_password(credentials.password, professor.password_hash):
        raise credentials_exception

    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": professor.professor_code, "role": "professor"},
        expires_delta=expires_delta,
    )

    return TokenResponse(access_token=access_token, token_type="bearer")


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: AdminLoginRequest,
    db: Session = Depends(get_db),
) -> Any:
    """
    Admin login endpoint.

    - Accepts username & password.
    - Verifies credentials against the Admin table.
    - Returns a JWT access token if valid.
    """

    # 1. Look up admin by username
    admin = (
        db.query(Admin)
        .filter(Admin.username == credentials.username)
        .first()
    )

    # Generic error to avoid leaking whether username or password is wrong
    invalid_credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if admin is None:
        raise invalid_credentials_exc

    # 2. Verify password using Argon2 helper
    if not verify_password(credentials.password, admin.password_hash):
        raise invalid_credentials_exc

    # 3. Credentials are valid -> issue JWT token
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    access_token = create_access_token(
        data={"sub": admin.username, "role": "admin"},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )


@router.post("/student/login", response_model=TokenResponse)
async def student_login(
    credentials: StudentLoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    # 1) Lookup student
    student = (
        db.query(Student)
        .filter(Student.student_number == credentials.student_number)
        .first()
    )

    # Use same error message for unknown user and wrong password
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect student number or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not student:
        raise credentials_exception

    # 2) Check active
    if not student.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student account is inactive",
        )

    # 3) Verify password
    if not verify_password(credentials.password, student.password_hash):
        raise credentials_exception

    # 4) Create JWT
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        data={"sub": student.student_number, "role": "student"},
        expires_delta=expires_delta,
    )

    return TokenResponse(access_token=token, token_type="bearer")



# "who am I?" test
@router.get("/me")
async def read_current_admin(
    current_admin: Admin = Depends(get_current_admin),
) -> dict:
    """
    Return basic info about the currently authenticated admin.
    Useful for testing JWT + get_current_admin.
    """
    return {
        "id": current_admin.id,
        "username": current_admin.username,
        "email": getattr(current_admin, "email", None),
        "is_active": getattr(current_admin, "is_active", None),
    }

