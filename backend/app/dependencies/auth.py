# backend/app/dependencies/auth.py

from __future__ import annotations

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.admin import Admin
from ..services.jwt import decode_access_token, InvalidTokenError


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
