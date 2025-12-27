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


def test_delete_legacy_requires_admin_auth(client: TestClient) -> None:
    resp = client.delete("/api/prerequisites/1-2")
    assert resp.status_code == 401


def test_delete_legacy_invalid_id_format_returns_400(client: TestClient, db_session: Session) -> None:
    token = get_admin_token(client, db_session)

    resp1 = client.delete("/api/prerequisites/abc", headers=_auth_headers(token))
    assert resp1.status_code == 400
    assert "Invalid id format" in resp1.json().get("detail", "")

    resp2 = client.delete("/api/prerequisites/1-abc", headers=_auth_headers(token))
    assert resp2.status_code == 400
    assert "Invalid id format" in resp2.json().get("detail", "")


def test_delete_legacy_not_found_returns_404(client: TestClient, db_session: Session) -> None:
    token = get_admin_token(client, db_session)

    resp = client.delete("/api/prerequisites/999-888", headers=_auth_headers(token))
    assert resp.status_code == 404


def test_delete_legacy_success_204_for_dash_format(client: TestClient, db_session: Session) -> None:
    token = get_admin_token(client, db_session)

    prereq = create_course(db_session, "PR")
    target = create_course(db_session, "TG")

    # Create relation via legacy POST (either key style is fine)
    create_resp = client.post(
        "/api/prerequisites",
        json={"course_id": target.id, "prereq_course_id": prereq.id},
        headers=_auth_headers(token),
    )
    assert create_resp.status_code in (200, 201), create_resp.text

    created = create_resp.json()
    legacy_id = created["id"]  # canonical dash format "{course_id}-{prereq_course_id}"

    del_resp = client.delete(f"/api/prerequisites/{legacy_id}", headers=_auth_headers(token))
    assert del_resp.status_code == 204, del_resp.text

    # Verify removed: GET should no longer include it
    get_resp = client.get("/api/prerequisites", headers=_auth_headers(token))
    assert get_resp.status_code == 200, get_resp.text
    items = get_resp.json()

    assert not any(x.get("id") == legacy_id for x in items)


def test_delete_legacy_success_for_colon_format(client: TestClient, db_session: Session) -> None:
    token = get_admin_token(client, db_session)

    prereq = create_course(db_session, "PR")
    target = create_course(db_session, "TG")

    create_resp = client.post(
        "/api/prerequisites",
        json={"target_course_id": target.id, "prerequisite_course_id": prereq.id},
        headers=_auth_headers(token),
    )
    assert create_resp.status_code in (200, 201), create_resp.text

    created = create_resp.json()
    dash_id = created["id"]
    course_id = created["course_id"]
    prereq_id = created["prereq_course_id"]

    colon_id = f"{course_id}:{prereq_id}"

    del_resp = client.delete(f"/api/prerequisites/{colon_id}", headers=_auth_headers(token))
    assert del_resp.status_code == 204, del_resp.text

    get_resp = client.get("/api/prerequisites", headers=_auth_headers(token))
    assert get_resp.status_code == 200, get_resp.text
    items = get_resp.json()

    assert not any(x.get("id") == dash_id for x in items)
