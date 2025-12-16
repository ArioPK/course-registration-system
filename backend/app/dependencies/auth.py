# backend/app/dependencies/auth.py

from __future__ import annotations

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.admin import Admin
from backend.app.models.student import Student
from backend.app.models.professor import Professor
from backend.app.services.jwt import decode_access_token, InvalidTokenError


# Student OAuth2 scheme (tokenUrl should match the student login endpoint)
# backend/tests/test_student_dependency.py

import uuid
from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.admin import Admin
from backend.app.models.student import Student
from backend.app.services.security import get_password_hash


def _auth_headers(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _unique_suffix() -> str:
    return uuid.uuid4().hex[:8]


def create_student_and_get_token(client: TestClient, db_session: Session) -> Dict[str, str]:
    suffix = _unique_suffix()
    student_number = f"stu_{suffix}"
    plain_password = "password123"

    student = Student(
        student_number=student_number,
        full_name="Test Student",
        email=f"student_{suffix}@example.com",
        national_id=f"NID_{suffix}",
        phone_number=f"0912{suffix[:7]}",
        major="Computer Engineering",
        entry_year=2023,
        units_taken=0,
        mark=None,
        password_hash=get_password_hash(plain_password),
        is_active=True,
    )
    db_session.add(student)
    db_session.commit()

    resp = client.post(
        "/auth/student/login",
        json={"student_number": student_number, "password": plain_password},
    )
    assert resp.status_code == 200, resp.text
    return {"student_number": student_number, "token": resp.json()["access_token"]}


def create_admin_and_get_token(client: TestClient, db_session: Session) -> str:
    suffix = _unique_suffix()
    username = f"admin_{suffix}"
    plain_password = "password123"

    admin = Admin(
        username=username,
        password_hash=get_password_hash(plain_password),
        national_id=f"nid_{suffix}",
        email=f"{username}@example.com",
        is_active=True,
    )
    db_session.add(admin)
    db_session.commit()

    resp = client.post("/auth/login", json={"username": username, "password": plain_password})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def test_get_current_student_rejects_invalid_token(client: TestClient) -> None:
    resp = client.get("/auth/student/me", headers={"Authorization": "Bearer invalidtoken"})
    assert resp.status_code == 401
    assert "detail" in resp.json()


def test_get_current_student_rejects_role_mismatch(client: TestClient, db_session: Session) -> None:
    admin_token = create_admin_and_get_token(client, db_session)
    resp = client.get("/auth/student/me", headers=_auth_headers(admin_token))
    assert resp.status_code == 403
    assert "detail" in resp.json()


def test_get_current_student_success(client: TestClient, db_session: Session) -> None:
    data = create_student_and_get_token(client, db_session)
    resp = client.get("/auth/student/me", headers=_auth_headers(data["token"]))

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["student_number"] == data["student_number"]
    assert "full_name" in body


student_bearer_scheme = HTTPBearer()


async def get_current_student(
    credentials: HTTPAuthorizationCredentials = Depends(student_bearer_scheme),
    db: Session = Depends(get_db),
) -> Student:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials

    try:
        payload = decode_access_token(token)
    except InvalidTokenError:
        raise credentials_exception

    sub = payload.get("sub")
    role = payload.get("role")

    if not sub or not role:
        raise credentials_exception

    if role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    student = db.query(Student).filter(Student.student_number == sub).first()
    if not student:
        raise credentials_exception

    if hasattr(student, "is_active") and not student.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive student account",
        )

    return student


# HTTP Bearer scheme – Swagger will show a simple "Value" field
bearer_scheme = HTTPBearer(auto_error=True)


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Admin:
    """
    Dependency that:
    - Extracts JWT access token from the Authorization header (Bearer <token>).
    - Decodes & validates the token.
    - Loads the corresponding Admin from the database.

    Raises HTTP 401 if:
    - Token is missing, invalid, or expired.
    - Token payload doesn't contain a 'sub' claim.
    - Admin with the given username doesn't exist.
    """
    # Common exception for credential issues
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # The raw JWT string
    token: str = credentials.credentials

    # 1) Decode token
    try:
        payload = decode_access_token(token)
    except InvalidTokenError:
        raise credentials_exception

    # 2) Extract subject (username)
    username: Optional[str] = payload.get("sub")
    if username is None:
        raise credentials_exception

    # 3) Look up admin in DB
    admin = (
        db.query(Admin)
        .filter(Admin.username == username)
        .first()
    )

    if admin is None:
        raise credentials_exception

    # 4) Return the current admin
    return admin


bearer_professor_scheme = HTTPBearer(auto_error=False)


def _raise_unauthorized(detail: str = "Could not validate credentials") -> None:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_professor(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_professor_scheme),
    db: Session = Depends(get_db),
) -> Professor:
    if credentials is None or not credentials.credentials:
        _raise_unauthorized("Not authenticated")

    token = credentials.credentials

    try:
        payload = decode_access_token(token)
    except Exception:
        _raise_unauthorized("Invalid or expired token")

    sub = payload.get("sub")
    role = payload.get("role")

    if not sub or not role:
        _raise_unauthorized("Token missing required claims")

    if role != "professor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    professor = (
        db.query(Professor)
        .filter(Professor.professor_code == sub)
        .first()
    )
    if professor is None:
        _raise_unauthorized("Professor not found")

    if hasattr(professor, "is_active") and professor.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive professor account",
        )

    return professor
