import uuid
from typing import Dict

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.admin import Admin
from backend.app.services.security import get_password_hash


def create_admin_and_get_token(client: TestClient, db_session: Session) -> str:
    """
    Create a test admin in the test database and obtain a valid JWT
    by calling the real /auth/login endpoint.

    Uses unique username/national_id per call to avoid UNIQUE constraint issues.
    """
    unique_suffix = uuid.uuid4().hex[:8]
    username = f"admin_{unique_suffix}"
    plain_password = "password123"

    admin = Admin(
        username=username,
        password_hash=get_password_hash(plain_password),
        national_id=f"nid_{unique_suffix}",
        email=f"{username}@example.com",
        is_active=True,
    )

    db_session.add(admin)
    db_session.commit()

    response = client.post(
        "/auth/login",
        json={
            "username": username,
            "password": plain_password,
        },
    )
    assert response.status_code == 200, f"Login failed in helper: {response.text}"

    data: Dict[str, str] = response.json()
    access_token = data.get("access_token")
    assert access_token, "No access_token returned from /auth/login"

    return access_token


def _auth_headers(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _sample_course_payload(code: str = "CS101") -> Dict:
    """
    Return a minimal valid CourseCreate payload.
    Adjust day_of_week value to match DayOfWeek enum values.
    """
    return {
        "code": code,
        "name": "Intro to Computer Science",
        "capacity": 30,
        "professor_name": "Dr. Test",
        "day_of_week": "MON",  # must match enum values
        "start_time": "09:00",
        "end_time": "10:30",
        "location": "Room 101",
    }


def test_create_course_with_valid_token(client: TestClient, db_session: Session) -> None:
    token = create_admin_and_get_token(client, db_session)
    payload = _sample_course_payload(code=f"CS{uuid.uuid4().hex[:4]}")

    response = client.post("/courses", json=payload, headers=_auth_headers(token))

    assert response.status_code == 201, response.text
    data = response.json()
    assert "id" in data
    assert data["code"] == payload["code"]
    assert data["name"] == payload["name"]
    assert data["capacity"] == payload["capacity"]
    assert data["professor_name"] == payload["professor_name"]


def test_list_courses_includes_created_course(client: TestClient, db_session: Session) -> None:
    token = create_admin_and_get_token(client, db_session)
    course_code = f"CS{uuid.uuid4().hex[:4]}"
    payload = _sample_course_payload(code=course_code)

    create_resp = client.post("/courses", json=payload, headers=_auth_headers(token))
    assert create_resp.status_code == 201, create_resp.text

    list_resp = client.get("/courses", headers=_auth_headers(token))
    assert list_resp.status_code == 200, list_resp.text

    courses = list_resp.json()
    assert isinstance(courses, list)
    assert any(course["code"] == course_code for course in courses)


def test_update_course_changes_data(client: TestClient, db_session: Session) -> None:
    token = create_admin_and_get_token(client, db_session)
    course_code = f"CS{uuid.uuid4().hex[:4]}"
    payload = _sample_course_payload(code=course_code)

    create_resp = client.post("/courses", json=payload, headers=_auth_headers(token))
    assert create_resp.status_code == 201, create_resp.text
    created = create_resp.json()
    course_id = created["id"]

    update_payload = {
        "name": "Updated Course Name",
        "capacity": 50,
    }

    update_resp = client.put(
        f"/courses/{course_id}",
        json=update_payload,
        headers=_auth_headers(token),
    )
    assert update_resp.status_code == 200, update_resp.text

    updated = update_resp.json()
    assert updated["id"] == course_id
    assert updated["name"] == "Updated Course Name"
    assert updated["capacity"] == 50
    # unchanged fields should remain the same
    assert updated["code"] == course_code


def test_delete_course_removes_it(client: TestClient, db_session: Session) -> None:
    token = create_admin_and_get_token(client, db_session)
    course_code = f"CS{uuid.uuid4().hex[:4]}"
    payload = _sample_course_payload(code=course_code)

    create_resp = client.post("/courses", json=payload, headers=_auth_headers(token))
    assert create_resp.status_code == 201, create_resp.text
    course_id = create_resp.json()["id"]

    delete_resp = client.delete(f"/courses/{course_id}", headers=_auth_headers(token))
    assert delete_resp.status_code in (200, 204)

    # Verify it is actually gone
    get_resp = client.get(f"/courses/{course_id}", headers=_auth_headers(token))
    assert get_resp.status_code == 404


def test_course_endpoints_require_token(client: TestClient, db_session: Session) -> None:
    # No Authorization header
    resp = client.get("/courses")
    assert resp.status_code == 401
    # Depending on your implementation, this may be "Not authenticated"
    assert "detail" in resp.json()


def test_course_endpoints_reject_invalid_token(client: TestClient, db_session: Session) -> None:
    headers = {"Authorization": "Bearer invalidtoken"}
    resp = client.get("/courses", headers=headers)

    assert resp.status_code == 401
    assert "detail" in resp.json()
