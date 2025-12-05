# backend/tests/test_auth_login.py

import uuid
from typing import Dict

import pytest
from sqlalchemy.orm import Session

from backend.app.models.admin import Admin
from backend.app.services.security import get_password_hash
from backend.app.services.jwt import decode_access_token


@pytest.fixture
def admin_credentials(db_session: Session) -> Dict[str, str]:
    """
    Create a test admin user in the test database and return its credentials.

    This fixture uses the db_session fixture from conftest.py, so it writes
    only to the test DB (never the real DB).
    """
    username = f"admin_test_{uuid.uuid4().hex[:8]}"
    plain_password = "password123"
    national_id = uuid.uuid4().hex[:10]
    
    admin = Admin(
        username=username,
        national_id=national_id,
        email=f"{username}@example.com",
        password_hash=get_password_hash(plain_password),
        is_active=True,
    )
    db_session.add(admin)
    db_session.commit()

    return {"username": username, "password": plain_password}


def test_admin_login_success(client, db_session: Session, admin_credentials: Dict[str, str]) -> None:
    """
    Login with correct credentials should return 200 and a JWT access token.
    """
    response = client.post(
        "/auth/login",
        json={
            "username": admin_credentials["username"],
            "password": admin_credentials["password"],
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert isinstance(data["access_token"], str)
    assert data["access_token"] != ""
    assert data.get("token_type") == "bearer"


def test_admin_login_wrong_password(client, db_session: Session, admin_credentials: Dict[str, str]) -> None:
    """
    Login with correct username but wrong password should fail with 401.
    """
    response = client.post(
        "/auth/login",
        json={
            "username": admin_credentials["username"],
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401
    data = response.json()
    # Match the detail text you used in the login endpoint
    assert data.get("detail") == "Incorrect username or password"


def test_admin_login_unknown_username(client, db_session: Session) -> None:
    """
    Login with a username that does not exist in the DB should fail with 401.
    """
    response = client.post(
        "/auth/login",
        json={
            "username": "no_such_user",
            "password": "whatever",
        },
    )

    assert response.status_code == 401
    data = response.json()
    assert data.get("detail") == "Incorrect username or password"


def test_admin_login_token_payload(client, db_session: Session, admin_credentials: Dict[str, str]) -> None:
    """
    After successful login, the JWT payload should contain the correct subject (sub).
    """
    response = client.post(
        "/auth/login",
        json={
            "username": admin_credentials["username"],
            "password": admin_credentials["password"],
        },
    )

    assert response.status_code == 200
    data = response.json()
    token = data["access_token"]

    payload = decode_access_token(token)
    assert payload.get("sub") == admin_credentials["username"]
