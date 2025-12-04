# backend/app/routers/auth.py

from __future__ import annotations

from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status # type: ignore
from sqlalchemy.orm import Session # type: ignore

from ..config.settings import settings
from ..database import get_db
from ..models.admin import Admin
from ..schemas.auth import AdminLoginRequest, TokenResponse # type: ignore
from ..services.security import verify_password
from ..services.jwt import create_access_token


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


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
        data={"sub": admin.username},
        expires_delta=access_token_expires,
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )
