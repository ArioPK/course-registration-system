import uuid
from datetime import time

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.course import Course
from backend.app.models.student import Student
from backend.app.services.security import get_password_hash


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _unique_suffix() -> str:
    return uuid.uuid4().hex[:8]


def create_student(db: Session) -> dict:
    suffix = _unique_suffix()
    student_number = f"stu_{suffix}"
    password = "student_pass123"

    s = Student(
        student_number=student_number,
        full_name="Student Test",
        email=f"{student_number}@example.com",
        national_id=f"nid_{suffix}",          # IMPORTANT: required by your DB (NOT NULL)
        phone_number="0000000000",
        major="CS",
        entry_year=2025,
        units_taken=0,
        mark=0,
        password_hash=get_password_hash(password),
        is_active=True,
    )
    db.add(s)
    db.commit()
    return {"student_number": student_number, "password": password}


def get_student_token(client: TestClient, creds: dict) -> str:
    resp = client.post("/auth/student/login", json=creds)
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def create_course(db: Session) -> Course:
    suffix = _unique_suffix()
    c = Course(
        code=f"CS{suffix}",
        name=f"Test Course {suffix}",
        capacity=30,
        professor_name="Dr. Test",
        day_of_week="MON",
        start_time=time(9, 0),     # IMPORTANT: SQLite needs datetime.time (not "09:00")
        end_time=time(10, 30),
        location="Room 101",
        is_active=True,
        units=3,
        department="CS",
        semester="1",
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def test_student_courses_requires_token(client: TestClient) -> None:
    resp = client.get("/api/student/courses")
    assert resp.status_code == 401


def test_student_can_list_courses_with_student_token(
    client: TestClient, db_session: Session
) -> None:
    course = create_course(db_session)
    creds = create_student(db_session)
    token = get_student_token(client, creds)

    resp = client.get("/api/student/courses", headers=_auth_headers(token))
    assert resp.status_code == 200, resp.text

    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    # Ensure our inserted course is present
    codes = {c["code"] for c in data}
    assert course.code in codes

    # Ensure CourseRead includes units
    first = data[0]
    assert "id" in first
    assert "code" in first
    assert "name" in first
    assert "capacity" in first
    assert "units" in first
