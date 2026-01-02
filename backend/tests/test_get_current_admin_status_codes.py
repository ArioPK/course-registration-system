import uuid
from typing import Dict, Tuple

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.student import Student
from backend.app.models.professor import Professor
from backend.app.services.security import get_password_hash


ADMIN_ONLY_ENDPOINT = "/api/admin/unit-limits"


def _auth_headers(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _sfx() -> str:
    return uuid.uuid4().hex[:8]


def create_student(db: Session, password: str = "password123") -> Tuple[Student, str]:
    s = _sfx()
    student = Student(
        student_number=f"stu_{s}",
        full_name="Status Code Student",
        email=f"stu_{s}@example.com",
        national_id=f"nid_{s}",
        password_hash=get_password_hash(password),
        units_taken=0,
        is_active=True,
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student, password


def create_professor(db: Session, password: str = "password123") -> Tuple[Professor, str]:
    s = _sfx()
    professor = Professor(
        professor_code=f"prof_{s}",
        full_name="Status Code Professor",
        email=f"prof_{s}@example.com",
        password_hash=get_password_hash(password),
        is_active=True,
    )
    db.add(professor)
    db.commit()
    db.refresh(professor)
    return professor, password


def get_student_token(client: TestClient, student: Student, password: str) -> str:
    resp = client.post(
        "/auth/student/login",
        json={"student_number": student.student_number, "password": password},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def get_professor_token(client: TestClient, professor: Professor, password: str) -> str:
    resp = client.post(
        "/auth/professor/login",
        json={"professor_code": professor.professor_code, "password": password},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def test_admin_endpoint_with_missing_token_returns_401(client: TestClient) -> None:
    resp = client.get(ADMIN_ONLY_ENDPOINT)
    assert resp.status_code == 401, resp.text


def test_admin_endpoint_with_invalid_token_returns_401(client: TestClient) -> None:
    resp = client.get(ADMIN_ONLY_ENDPOINT, headers=_auth_headers("badtoken"))
    assert resp.status_code == 401, resp.text


def test_admin_endpoint_with_student_token_returns_403(
    client: TestClient, db_session: Session
) -> None:
    student, pw = create_student(db_session)
    token = get_student_token(client, student, pw)

    resp = client.get(ADMIN_ONLY_ENDPOINT, headers=_auth_headers(token))
    assert resp.status_code == 403, resp.text


def test_admin_endpoint_with_professor_token_returns_403(
    client: TestClient, db_session: Session
) -> None:
    professor, pw = create_professor(db_session)
    token = get_professor_token(client, professor, pw)

    resp = client.get(ADMIN_ONLY_ENDPOINT, headers=_auth_headers(token))
    assert resp.status_code == 403, resp.text
