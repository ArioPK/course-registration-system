import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.professor import Professor
from backend.app.models.student import Student
from backend.app.services.security import get_password_hash


def _suffix() -> str:
    return uuid.uuid4().hex[:8]


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _create_professor_and_get_token(client: TestClient, db_session: Session) -> tuple[str, str]:
    s = _suffix()
    code = f"ptest_{s}"
    password = "prof_password123"

    prof = Professor(
        professor_code=code,
        full_name="Prof Test",
        email=f"prof_{s}@example.com",
        password_hash=get_password_hash(password),
        is_active=True,
    )
    db_session.add(prof)
    db_session.commit()

    resp = client.post("/auth/professor/login", json={"professor_code": code, "password": password})
    assert resp.status_code == 200, resp.text
    return code, resp.json()["access_token"]


def _create_student_and_get_token(client: TestClient, db_session: Session) -> str:
    s = _suffix()
    student_number = f"stu_{s}"
    password = "student_password123"

    student = Student(
        student_number=student_number,
        full_name="Student Test",
        email=f"stu_{s}@example.com",
        national_id=f"NID_{s}",
        phone_number=f"0912{s[:6]}",
        major="CS",
        entry_year=2023,
        units_taken=0,
        mark=None,
        password_hash=get_password_hash(password),
        is_active=True,
    )
    db_session.add(student)
    db_session.commit()

    resp = client.post("/auth/student/login", json={"student_number": student_number, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def test_get_current_professor_success(client: TestClient, db_session: Session) -> None:
    code, token = _create_professor_and_get_token(client, db_session)

    me_resp = client.get("/auth/professor/me", headers=_auth_headers(token))
    assert me_resp.status_code == 200, me_resp.text
    data = me_resp.json()
    assert data["professor_code"] == code


def test_get_current_professor_rejects_invalid_token(client: TestClient) -> None:
    resp = client.get("/auth/professor/me", headers={"Authorization": "Bearer invalidtoken"})
    assert resp.status_code == 401
    assert "detail" in resp.json()


def test_get_current_professor_rejects_role_mismatch(client: TestClient, db_session: Session) -> None:
    student_token = _create_student_and_get_token(client, db_session)

    resp = client.get("/auth/professor/me", headers=_auth_headers(student_token))
    assert resp.status_code == 403
    assert "detail" in resp.json()
