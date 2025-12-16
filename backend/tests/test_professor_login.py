import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.professor import Professor
from backend.app.services.jwt import decode_access_token
from backend.app.services.security import get_password_hash


def _unique_suffix() -> str:
    return uuid.uuid4().hex[:8]


def test_professor_login_success(client: TestClient, db_session: Session) -> None:
    suffix = _unique_suffix()
    code = f"ptest_{suffix}"
    password = "prof_password123"

    prof = Professor(
        professor_code=code,
        full_name="Prof Test",
        email=f"prof_{suffix}@example.com",
        password_hash=get_password_hash(password),
        is_active=True,
    )
    db_session.add(prof)
    db_session.commit()

    response = client.post(
        "/auth/professor/login",
        json={"professor_code": code, "password": password},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)
    assert data["access_token"] != ""


def test_professor_login_wrong_password(client: TestClient, db_session: Session) -> None:
    suffix = _unique_suffix()
    code = f"ptest_{suffix}"

    prof = Professor(
        professor_code=code,
        full_name="Prof Test",
        email=f"prof_{suffix}@example.com",
        password_hash=get_password_hash("correct_password"),
        is_active=True,
    )
    db_session.add(prof)
    db_session.commit()

    response = client.post(
        "/auth/professor/login",
        json={"professor_code": code, "password": "wrong_password"},
    )
    assert response.status_code == 401
    assert "detail" in response.json()


def test_professor_login_unknown_professor(client: TestClient) -> None:
    response = client.post(
        "/auth/professor/login",
        json={"professor_code": "unknown_code", "password": "whatever"},
    )
    assert response.status_code == 401
    assert "detail" in response.json()


def test_professor_login_token_contains_role_and_sub(
    client: TestClient, db_session: Session
) -> None:
    suffix = _unique_suffix()
    code = f"ptest_{suffix}"
    password = "prof_password123"

    prof = Professor(
        professor_code=code,
        full_name="Prof Test",
        email=f"prof_{suffix}@example.com",
        password_hash=get_password_hash(password),
        is_active=True,
    )
    db_session.add(prof)
    db_session.commit()

    response = client.post(
        "/auth/professor/login",
        json={"professor_code": code, "password": password},
    )
    assert response.status_code == 200

    token = response.json()["access_token"]
    payload = decode_access_token(token)

    assert payload["sub"] == code
    assert payload["role"] == "professor"
