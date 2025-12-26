# backend/tests/test_student_courses_catalog.py

import uuid
from datetime import time

import pytest
from starlette.testclient import TestClient
from sqlalchemy.orm import Session
from typing import Dict

from backend.app.models.course import Course
from backend.app.models.student import Student
from backend.app.services.security import get_password_hash 


def _auth_headers(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def create_student(db: Session) -> Student:
    sn = f"stu_{uuid.uuid4().hex[:8]}"
    student = Student(
        student_number=sn,
        full_name="Student Test",
        email=f"{sn}@example.com",
        national_id=f"nid_{uuid.uuid4().hex[:10]}",  # required in your schema
        phone_number="0000000000",
        major="CS",
        entry_year=2024,
        units_taken=0,
        mark=0,
        password_hash=get_password_hash("pass1234"),
        is_active=True,
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


def get_student_token(client: TestClient, db: Session) -> str:
    student = create_student(db)

    payload = {"student_number": student.student_number, "password": "pass1234"}

    # Try JSON first, fallback to form if your endpoint uses OAuth2PasswordRequestForm
    resp = client.post("/api/auth/student/login", json=payload)
    if resp.status_code == 404:
        # if your app has no /api prefix, fallback
        resp = client.post("/auth/student/login", json=payload)

    if resp.status_code == 422:
        resp = client.post("/api/auth/student/login", data=payload)
        if resp.status_code == 404:
            resp = client.post("/auth/student/login", data=payload)

    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def create_course(db: Session, *, code: str, name: str, professor_name: str) -> Course:
    course = Course(
        code=code,
        name=name,
        capacity=30,
        professor_name=professor_name,
        day_of_week="MON",
        start_time=time(9, 0),
        end_time=time(10, 30),
        location="Room 101",
        is_active=True,
        units=3,
        department="CS",
        semester="1",
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


def seed_courses(db: Session):
    a = create_course(
        db,
        code=f"CS{uuid.uuid4().hex[:6].upper()}",
        name="Intro to CS",
        professor_name="Dr. Alice",
    )
    b = create_course(
        db,
        code=f"CS{uuid.uuid4().hex[:6].upper()}",
        name="Data Structures",
        professor_name="Prof. Bob",
    )
    c = create_course(
        db,
        code=f"CS{uuid.uuid4().hex[:6].upper()}",
        name="advanced databases",
        professor_name="Dr. ALICE",
    )
    return a, b, c


def test_search_by_q_matches_course_name_case_insensitive_partial(
    client: TestClient, db_session: Session
) -> None:
    token = get_student_token(client, db_session)
    intro, _, _ = seed_courses(db_session)

    resp = client.get(
        "/api/student/courses?q=intro",
        headers=_auth_headers(token),
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert isinstance(data, list)
    assert any(item["id"] == intro.id for item in data)
    # should not return all 3 if filter works
    assert all("intro" in item["name"].lower() or "intro" in item.get("professor_name", "").lower() for item in data)


def test_search_by_q_matches_professor_name_case_insensitive_partial(
    client: TestClient, db_session: Session
) -> None:
    token = get_student_token(client, db_session)
    a, _, c = seed_courses(db_session)

    resp = client.get(
        "/api/student/courses?q=alice",
        headers=_auth_headers(token),
    )
    assert resp.status_code == 200, resp.text
    ids = {item["id"] for item in resp.json()}
    assert a.id in ids
    assert c.id in ids


def test_search_with_skip_limit_paginates(client: TestClient, db_session: Session) -> None:
    token = get_student_token(client, db_session)
    seed_courses(db_session)

    resp1 = client.get("/api/student/courses?skip=0&limit=2", headers=_auth_headers(token))
    assert resp1.status_code == 200, resp1.text
    data1 = resp1.json()
    assert len(data1) == 2

    resp2 = client.get("/api/student/courses?skip=2&limit=2", headers=_auth_headers(token))
    assert resp2.status_code == 200, resp2.text
    data2 = resp2.json()
    assert len(data2) >= 1

    # No overlap if ordering is stable (we order by id.asc() in repo)
    ids1 = {x["id"] for x in data1}
    ids2 = {x["id"] for x in data2}
    assert ids1.isdisjoint(ids2)


def test_search_empty_q_behaves_like_no_filter(client: TestClient, db_session: Session) -> None:
    token = get_student_token(client, db_session)
    seed_courses(db_session)

    resp = client.get("/api/student/courses?q=   ", headers=_auth_headers(token))
    assert resp.status_code == 200, resp.text
    assert len(resp.json()) >= 3
