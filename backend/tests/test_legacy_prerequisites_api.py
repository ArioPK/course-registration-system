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


def get_admin_token(client: TestClient, db_session: Session) -> str:
    s = _suffix()
    username = f"admin_{s}"
    password = "password123"

    admin = Admin(
        username=username,
        password_hash=get_password_hash(password),
        national_id=f"nid_{s}",
        email=f"{username}@example.com",
        is_active=True,
    )
    db_session.add(admin)
    db_session.commit()

    resp = client.post("/auth/login", json={"username": username, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def create_course(db_session: Session, code_prefix: str) -> Course:
    s = _suffix()
    course = Course(
        code=f"{code_prefix}{s[:4]}",
        name=f"Legacy Prereq Course {s}",
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


def test_get_legacy_prerequisites_requires_admin_auth(client: TestClient) -> None:
    resp = client.get("/api/prerequisites")
    assert resp.status_code == 401


def test_post_legacy_prerequisites_requires_admin_auth(client: TestClient) -> None:
    resp = client.post("/api/prerequisites", json={"target_course_id": 1, "prerequisite_course_id": 2})
    assert resp.status_code == 401


def test_post_legacy_prerequisites_accepts_frontend_keys(client: TestClient, db_session: Session) -> None:
    token = get_admin_token(client, db_session)
    prereq = create_course(db_session, "PR")
    target = create_course(db_session, "TG")

    resp = client.post(
        "/api/prerequisites",
        json={"target_course_id": target.id, "prerequisite_course_id": prereq.id},
        headers=_auth_headers(token),
    )
    assert resp.status_code in (200, 201), resp.text

    data = resp.json()
    # Both key styles must be present
    assert data["course_id"] == target.id
    assert data["prereq_course_id"] == prereq.id
    assert data["target_course_id"] == target.id
    assert data["prerequisite_course_id"] == prereq.id


def test_post_legacy_prerequisites_accepts_backend_keys(client: TestClient, db_session: Session) -> None:
    token = get_admin_token(client, db_session)
    prereq = create_course(db_session, "PR")
    target = create_course(db_session, "TG")

    resp = client.post(
        "/api/prerequisites",
        json={"course_id": target.id, "prereq_course_id": prereq.id},
        headers=_auth_headers(token),
    )
    assert resp.status_code in (200, 201), resp.text

    data = resp.json()
    assert data["course_id"] == target.id
    assert data["prereq_course_id"] == prereq.id
    assert data["target_course_id"] == target.id
    assert data["prerequisite_course_id"] == prereq.id


def test_get_legacy_prerequisites_returns_list_with_alias_keys(client: TestClient, db_session: Session) -> None:
    token = get_admin_token(client, db_session)
    prereq = create_course(db_session, "PR")
    target = create_course(db_session, "TG")

    create_resp = client.post(
        "/api/prerequisites",
        json={"course_id": target.id, "prereq_course_id": prereq.id},
        headers=_auth_headers(token),
    )
    assert create_resp.status_code in (200, 201), create_resp.text

    get_resp = client.get("/api/prerequisites", headers=_auth_headers(token))
    assert get_resp.status_code == 200, get_resp.text

    items = get_resp.json()
    assert isinstance(items, list)

    # Don't assume list length because the test DB persists across tests; just assert our relation exists.
    assert any(
        x.get("course_id") == target.id
        and x.get("prereq_course_id") == prereq.id
        and x.get("target_course_id") == target.id
        and x.get("prerequisite_course_id") == prereq.id
        for x in items
    )
