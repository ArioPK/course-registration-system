# backend/app/schemas/auth.py

from __future__ import annotations

from pydantic import BaseModel # type: ignore


class AdminLoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
