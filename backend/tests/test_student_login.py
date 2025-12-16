# backend/tests/test_student_login.py
import uuid
import pytest

from sqlalchemy.orm import Session

from backend.app.models.student import Student
from backend.app.services.security import get_password_hash
from backend.app.services.jwt import decode_access_token

@pytest.fixture
def student_credentials(db_session: Session) -> dict:
    suffix = uuid.uuid4().hex[:8]
    student_number = f"stu_test_{suffix}"
    plain_password = "password123"

    student = Student(
        student_number=student_number,
        full_name="Test Student",
        email=f"student_{suffix}@example.com",
        national_id=f"NID_{suffix}",
        phone_number="09120000001",
        major="Computer Engineering",
        entry_year=2023,
        units_taken=0,
        mark=None,
        password_hash=get_password_hash(plain_password),
        is_active=True,
    )
    db_session.add(student)
    db_session.commit()

    return {"student_number": student_number, "password": plain_password}


def test_student_login_token_contains_student_role(client, student_credentials) -> None:
    resp = client.post("/auth/student/login", json=student_credentials)
    assert resp.status_code == 200, resp.text

    token = resp.json()["access_token"]
    payload = decode_access_token(token)

    assert payload["sub"] == student_credentials["student_number"]
    assert payload["role"] == "student"
