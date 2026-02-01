# backend/tests/test_professor_courses_api.py

from datetime import time

import pytest

from backend.app.models.course import Course
from backend.app.services.jwt import create_access_token
from backend.tests.test_enrollment_service import _new_id

# Adjust this import if your Professor model lives elsewhere
from backend.app.models.professor import Professor

CURRENT_TERM = "1404-1"


def professor_auth_headers(professor: Professor) -> dict:
    token = create_access_token(data={"sub": professor.professor_code, "role": "professor"})
    return {"Authorization": f"Bearer {token}"}


def student_auth_headers() -> dict:
    token = create_access_token(data={"sub": "S00001", "role": "student"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def professor(db_session) -> Professor:
    i = _new_id()
    prof_number = f"P{i:05d}"

    p = Professor(
        professor_code=prof_number,
        full_name="Dr. Alice   Smith",  # intentionally odd spacing
        # national_id=f"{i:010d}",
        email=f"{prof_number}@test.local",
        # phone_number="09120000000",
        # department="CS",
        password_hash="x",
        is_active=True,
    )
    db_session.add(p)
    db_session.commit()
    return p


def _make_course(
    db_session,
    *,
    code: str,
    professor_name: str,
    semester: str,
) -> Course:
    c = Course(
        code=code,
        name=f"Course {code}",
        capacity=30,
        professor_name=professor_name,
        day_of_week="MON",
        start_time=time(9, 0),
        end_time=time(10, 0),
        location="Room 101",
        is_active=True,
        units=3,
        department="CS",
        semester=semester,
    )
    db_session.add(c)
    db_session.commit()
    return c


def test_professor_sees_only_own_courses_current_term_sorted(client, db_session, monkeypatch, professor):
    monkeypatch.setenv("CURRENT_TERM", CURRENT_TERM)

    # Should appear (current term + name match; case + whitespace differences)
    c1 = _make_course(
        db_session,
        code="CS101",
        professor_name="  dr.  alice smith  ",  # normalized match
        semester=CURRENT_TERM,
    )
    c2 = _make_course(
        db_session,
        code="CS099",
        professor_name="DR. ALICE   SMITH",  # normalized match
        semester=CURRENT_TERM,
    )

    # Should NOT appear (wrong term)
    _make_course(
        db_session,
        code="CS555",
        professor_name="Dr. Alice Smith",
        semester="1404-2",
    )

    # Should NOT appear (different professor)
    _make_course(
        db_session,
        code="CS777",
        professor_name="Dr. Bob Jones",
        semester=CURRENT_TERM,
    )

    resp = client.get(
        "/api/professor/courses",
        headers=professor_auth_headers(professor),
    )

    assert resp.status_code == 200, resp.text
    body = resp.json()

    returned_ids = [c["id"] for c in body]
    assert set(returned_ids) == {c1.id, c2.id}

    # Sorted by code asc (CS099 then CS101)
    returned_codes = [c["code"] for c in body]
    assert returned_codes == ["CS099", "CS101"]


def test_professor_courses_auth_no_token_401(client):
    resp = client.get("/api/professor/courses")
    assert resp.status_code == 401, resp.text


def test_professor_courses_auth_role_mismatch_403(client):
    resp = client.get("/api/professor/courses", headers=student_auth_headers())
    assert resp.status_code == 403, resp.text