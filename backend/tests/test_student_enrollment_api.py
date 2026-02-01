# backend/tests/test_student_enrollment_api.py

from datetime import time

import pytest

from backend.app.models.course import Course
from backend.app.models.student import Student
from backend.app.services.jwt import create_access_token
from backend.tests.test_enrollment_service import _new_id


@pytest.fixture
def student(db_session) -> Student:
    i = _new_id()
    national_id = f"{i:010d}"
    student_number = f"S{i:05d}"

    student = Student(
        student_number=student_number,
        full_name=f"Student {i}",
        national_id=national_id,
        email=f"{student_number}@test.local",
        phone_number="09120000000",
        major="CS",
        entry_year=1400,
        units_taken=0,
        password_hash="x",
        is_active=True,
    )
    db_session.add(student)
    db_session.commit()
    return student


@pytest.fixture
def course(db_session) -> Course:
    i = _new_id()
    course = Course(
        code=f"CS{i:03d}",
        name=f"Test Course {i}",
        capacity=30,
        professor_name="Test Prof",
        day_of_week="MON",
        start_time=time(9, 0),
        end_time=time(10, 0),
        location="Room 101",
        is_active=True,
        units=3,
        department="CS",
        semester="1404-2",
    )
    db_session.add(course)
    db_session.commit()
    return course


def student_auth_headers(student: Student) -> dict:
    token = create_access_token(data={"sub": student.student_number, "role": "student"})
    return {"Authorization": f"Bearer {token}"}


def test_enroll_student_success(client, student, course):
    enrollment_data = {"course_id": course.id, "term": "1404-2"}

    resp = client.post(
        "/api/student/enrollments",
        json=enrollment_data,
        headers=student_auth_headers(student),
    )

    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["course_id"] == course.id
    assert body["student_id"] == student.id


def test_enroll_student_course_not_found(client, student):
    enrollment_data = {"course_id": 999999, "term": "1404-2"}

    resp = client.post(
        "/api/student/enrollments",
        json=enrollment_data,
        headers=student_auth_headers(student),
    )

    assert resp.status_code == 404, resp.text
    assert resp.json()["detail"] == "The requested course was not found."