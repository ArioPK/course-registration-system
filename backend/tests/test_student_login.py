# backend/tests/test_student_login.py
import uuid
import pytest
from sqlalchemy.orm import Session

from backend.app.models.student import Student
from backend.app.services.security import get_password_hash

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
