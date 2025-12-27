# backend/app/services/jwt.py

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import JWTError, jwt # type: ignore

from ..config.settings import settings


class InvalidTokenError(Exception):
    """Raised when a JWT access token is invalid or cannot be decoded."""
    pass


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a signed JWT access token.

    Args:
        data: The payload data to include in the token (e.g. {"sub": "admin_username"}).
        expires_delta: Optional custom expiration delta. If not provided,
                       settings.ACCESS_TOKEN_EXPIRE_MINUTES will be used.

    Returns:
        Encoded JWT as a string.
    """
    to_encode = data.copy()

    # Determine expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    # Add standard "exp" claim
    to_encode["exp"] = expire

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT access token.

    Args:
        token: The encoded JWT string.

    Returns:
        The decoded payload as a dict.

    Raises:
        InvalidTokenError: If the token is invalid, expired, or cannot be decoded.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )

        # Check that 'sub' exists in the payload, it's important for identifying the user
        if "sub" not in payload:
            raise InvalidTokenError("Token payload missing 'sub' claim")

        # Optionally check token expiration manually if needed
        # (in case you want to handle expired tokens differently)
        if datetime.utcnow() > datetime.utcfromtimestamp(payload["exp"]):
            raise InvalidTokenError("Token has expired")

        return payload

    except JWTError as exc:
        raise InvalidTokenError("Invalid or expired access token") from exc
