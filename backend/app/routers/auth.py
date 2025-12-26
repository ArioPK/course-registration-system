# backend/app/routers/auth.py

from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from backend.app.config.settings import settings
from backend.app.database import get_db
from backend.app.dependencies.auth import (
    get_current_admin,
    get_current_professor,
    get_current_student,
)
from backend.app.models.admin import Admin
from backend.app.models.professor import Professor
from backend.app.models.student import Student
from backend.app.schemas.auth import (
    AdminLoginRequest,
    ProfessorLoginRequest,
    StudentLoginRequest,
    TokenResponse,
    UserContext,
)
from backend.app.services.auth_service import (
    authenticate_any_role,
    InvalidCredentialsError,
    InactiveAccountError,
)
from backend.app.schemas.auth import UserContext
from backend.app.services.jwt import create_access_token
from backend.app.services.security import verify_password


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.get("/student/me")
def student_me(current_student: Student = Depends(get_current_student)):
    """
    TEMP: verify student auth dependency works end-to-end.
    """
    return {
        "student_number": current_student.student_number,
        "full_name": current_student.full_name,
    }


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

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserContext(
            role="professor",
            identifier=professor.professor_code,
            id=getattr(professor, "id", None),
        ),
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: AdminLoginRequest,  # must remain {username, password}
    db: Session = Depends(get_db),
) -> TokenResponse:
    """
    Unified login shim (backend-only):

    Accepts {username, password} and authenticates by precedence:
      1) Admin.username == username
      2) Student.student_number == username
      3) Professor.professor_code == username

    Collision behavior:
      - Admin wins. If an Admin exists with this identifier, we do NOT try Student/Professor.
        Wrong password returns 401 (generic) even if a Student/Professor with the same identifier exists.
    """

    invalid_credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        auth = authenticate_any_role(db, credentials.username, credentials.password)
    except InactiveAccountError:
        # Keep consistent with existing pattern (student/prof dedicated endpoints use 403).
        # Use a generic message to avoid revealing role.
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )
    except InvalidCredentialsError:
        raise invalid_credentials_exc

    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": auth.identifier, "role": auth.role},
        expires_delta=expires_delta,
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserContext(role=auth.role, identifier=auth.identifier, id=auth.id),
    )


@router.post("/student/login", response_model=TokenResponse)
async def student_login(
    credentials: StudentLoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    student = (
        db.query(Student)
        .filter(Student.student_number == credentials.student_number)
        .first()
    )

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect student number or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not student:
        raise credentials_exception

    if not student.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student account is inactive",
        )

    if not verify_password(credentials.password, student.password_hash):
        raise credentials_exception

    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        data={"sub": student.student_number, "role": "student"},
        expires_delta=expires_delta,
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserContext(
            role="student",
            identifier=student.student_number,
            id=getattr(student, "id", None),
        ),
    )


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


@router.get("/professor/me")
def professor_me(current_professor: Professor = Depends(get_current_professor)):
    return {
        "professor_code": current_professor.professor_code,
        "full_name": current_professor.full_name,
    }
