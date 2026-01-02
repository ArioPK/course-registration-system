# backend/tests/test_course_enrolled_field.py

import uuid
from datetime import time
from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.admin import Admin
from backend.app.models.course import Course
from backend.app.services.security import get_password_hash


def _auth_headers(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _suffix() -> str:
    return uuid.uuid4().hex[:8]


def create_admin(db_session: Session, password: str = "password123") -> Admin:
    s = _suffix()
    admin = Admin(
        username=f"admin_{s}",
        password_hash=get_password_hash(password),
        national_id=f"nid_{s}",
        email=f"admin_{s}@example.com",
        is_active=True,
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


def get_admin_token(client: TestClient, username: str, password: str) -> str:
    resp = client.post("/auth/login", json={"username": username, "password": password})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "access_token" in data
    return data["access_token"]


def create_course(db_session: Session) -> Course:
    s = _suffix()
    course = Course(
        code=f"CS{s[:4]}",
        name=f"Enrolled Shim Course {s}",
        capacity=30,
        professor_name="Dr. Shim",
        day_of_week="SAT",
        start_time=time(9, 0),
        end_time=time(11, 0),
        location="Room 1",
        units=3,
        department="CS",
        semester="Fall",
        is_active=True,
    )
    db_session.add(course)
    db_session.commit()
    db_session.refresh(course)
    return course


def test_course_list_includes_enrolled_field(client: TestClient, db_session: Session) -> None:
    # Arrange
    admin = create_admin(db_session)
    token = get_admin_token(client, admin.username, "password123")
    create_course(db_session)

    # Act
    resp = client.get("/api/courses", headers=_auth_headers(token))
    assert resp.status_code == 200, resp.text

    # Assert
    items = resp.json()
    assert isinstance(items, list)
    assert len(items) >= 1
    for item in items:
        assert "enrolled" in item
        assert item["enrolled"] == 0


def test_course_detail_includes_enrolled_field(client: TestClient, db_session: Session) -> None:
    # Arrange
    admin = create_admin(db_session)
    token = get_admin_token(client, admin.username, "password123")
    course = create_course(db_session)

    # Act
    resp = client.get(f"/api/courses/{course.id}", headers=_auth_headers(token))
    assert resp.status_code == 200, resp.text

    # Assert
    data = resp.json()
    assert "enrolled" in data
    assert data["enrolled"] == 0
