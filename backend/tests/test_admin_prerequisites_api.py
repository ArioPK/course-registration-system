import uuid
from datetime import time
from typing import Dict

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.admin import Admin
from backend.app.models.course import Course
from backend.app.models.student import Student
from backend.app.services.security import get_password_hash


def _auth_headers(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _unique_suffix() -> str:
    return uuid.uuid4().hex[:8]


def get_admin_token(client: TestClient, db_session: Session) -> str:
    suffix = _unique_suffix()
    username = f"admin_{suffix}"
    password = "password123"

    admin = Admin(
        username=username,
        password_hash=get_password_hash(password),
        national_id=f"nid_{suffix}",
        email=f"{username}@example.com",
        is_active=True,
    )
    db_session.add(admin)
    db_session.commit()

    resp = client.post("/auth/login", json={"username": username, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def get_student_token(client: TestClient, db_session: Session) -> str:
    suffix = _unique_suffix()
    student_number = f"stu_{suffix}"
    password = "student123"

    student = Student(
        student_number=student_number,
        full_name="Student Test",
        email=f"{student_number}@example.com",
        national_id=f"nid_{suffix}",  # ✅ required NOT NULL
        password_hash=get_password_hash(password),
        is_active=True,
    )
    db_session.add(student)
    db_session.commit()

    resp = client.post("/auth/student/login", json={"student_number": student_number, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def create_course(db_session: Session, code_prefix: str = "CS") -> Course:
    suffix = _unique_suffix()
    course = Course(
        code=f"{code_prefix}{suffix[:4]}",
        name=f"Test Course {suffix}",
        units=3,
        department="CS",
        semester="1",
        capacity=30,
        professor_name="Dr. Test",
        day_of_week="MON",
        start_time=time(9, 0),
        end_time=time(10, 30),
        location="Room 101",
        is_active=True,
    )
    db_session.add(course)
    db_session.commit()
    db_session.refresh(course)
    return course


def test_prereq_endpoints_require_admin_auth(client: TestClient, db_session: Session) -> None:
    course = create_course(db_session)
    resp = client.get(f"/api/courses/{course.id}/prerequisites")
    assert resp.status_code == 401


def test_admin_can_add_and_list_prerequisites(client: TestClient, db_session: Session) -> None:
    token = get_admin_token(client, db_session)
    prereq = create_course(db_session, code_prefix="PR")
    target = create_course(db_session, code_prefix="TG")

    add_resp = client.post(
        f"/api/courses/{target.id}/prerequisites",
        json={"course_id": target.id, "prereq_course_id": prereq.id},
        headers=_auth_headers(token),
    )
    assert add_resp.status_code == 201, add_resp.text
    data = add_resp.json()
    assert data["course_id"] == target.id
    assert data["prereq_course_id"] == prereq.id

    list_resp = client.get(
        f"/api/courses/{target.id}/prerequisites",
        headers=_auth_headers(token),
    )
    assert list_resp.status_code == 200, list_resp.text
    items = list_resp.json()
    assert any(x["course_id"] == target.id and x["prereq_course_id"] == prereq.id for x in items)


def test_admin_can_remove_prerequisite(client: TestClient, db_session: Session) -> None:
    token = get_admin_token(client, db_session)
    prereq = create_course(db_session, code_prefix="PR")
    target = create_course(db_session, code_prefix="TG")

    add_resp = client.post(
        f"/api/courses/{target.id}/prerequisites",
        json={"course_id": target.id, "prereq_course_id": prereq.id},
        headers=_auth_headers(token),
    )
    assert add_resp.status_code == 201, add_resp.text

    del_resp = client.delete(
        f"/api/courses/{target.id}/prerequisites/{prereq.id}",
        headers=_auth_headers(token),
    )
    assert del_resp.status_code == 204, del_resp.text

    list_resp = client.get(
        f"/api/courses/{target.id}/prerequisites",
        headers=_auth_headers(token),
    )
    assert list_resp.status_code == 200
    assert all(x["prereq_course_id"] != prereq.id for x in list_resp.json())


def test_add_prereq_rejects_self_prereq(client: TestClient, db_session: Session) -> None:
    token = get_admin_token(client, db_session)
    c = create_course(db_session)

    resp = client.post(
        f"/api/courses/{c.id}/prerequisites",
        json={"course_id": c.id, "prereq_course_id": c.id},
        headers=_auth_headers(token),
    )

    assert resp.status_code == 422, resp.text
    # ensures validation message is present
    assert "self-prerequisite" in resp.text.lower()


def test_add_prereq_rejects_duplicates(client: TestClient, db_session: Session) -> None:
    token = get_admin_token(client, db_session)
    prereq = create_course(db_session, code_prefix="PR")
    target = create_course(db_session, code_prefix="TG")

    first = client.post(
        f"/api/courses/{target.id}/prerequisites",
        json={"course_id": target.id, "prereq_course_id": prereq.id},
        headers=_auth_headers(token),
    )
    assert first.status_code == 201, first.text

    second = client.post(
        f"/api/courses/{target.id}/prerequisites",
        json={"course_id": target.id, "prereq_course_id": prereq.id},
        headers=_auth_headers(token),
    )
    assert second.status_code == 409, second.text


def test_add_prereq_course_not_found(client: TestClient, db_session: Session) -> None:
    token = get_admin_token(client, db_session)
    prereq = create_course(db_session, code_prefix="PR")

    resp = client.post(
        f"/api/courses/999999/prerequisites",
        json={"course_id": 999999, "prereq_course_id": prereq.id},
        headers=_auth_headers(token),
    )
    assert resp.status_code == 404, resp.text


def test_prereq_endpoints_reject_non_admin_token(client: TestClient, db_session: Session) -> None:
    # Optional but useful: verify admin-only enforcement using a student token.
    token = get_student_token(client, db_session)
    course = create_course(db_session)

    resp = client.get(
        f"/api/courses/{course.id}/prerequisites",
        headers=_auth_headers(token),
    )
    assert resp.status_code in (401, 403), resp.text
