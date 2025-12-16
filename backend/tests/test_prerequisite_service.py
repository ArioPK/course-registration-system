# backend/tests/test_prerequisite_service.py

import uuid
from datetime import time

import pytest
from sqlalchemy.orm import Session

from backend.app.models.course import Course
from backend.app.services.prerequisite_service import (
    add_prerequisite_service,
    list_prerequisites_service,
    remove_prerequisite_service,
    PrerequisiteNotFoundError,
    DuplicatePrerequisiteError,
    InvalidPrerequisiteRelationError,
)


def _unique_code(prefix: str = "CS") -> str:
    return f"{prefix}{uuid.uuid4().hex[:6].upper()}"


def _create_course(db: Session, code: str) -> Course:
    course = Course(
        code=code,
        name=f"Test Course {code}",
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
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


def test_add_prereq_rejects_self_prereq(db_session: Session) -> None:
    with pytest.raises(InvalidPrerequisiteRelationError):
        add_prerequisite_service(db_session, course_id=1, prereq_course_id=1)


def test_add_prereq_requires_course_exists(db_session: Session) -> None:
    prereq = _create_course(db_session, _unique_code())
    with pytest.raises(PrerequisiteNotFoundError, match="Course not found"):
        add_prerequisite_service(db_session, course_id=999999, prereq_course_id=prereq.id)


def test_add_prereq_requires_prereq_course_exists(db_session: Session) -> None:
    course = _create_course(db_session, _unique_code())
    with pytest.raises(PrerequisiteNotFoundError, match="Prerequisite course not found"):
        add_prerequisite_service(db_session, course_id=course.id, prereq_course_id=999999)


def test_add_prereq_rejects_duplicates(db_session: Session) -> None:
    c1 = _create_course(db_session, _unique_code())
    c2 = _create_course(db_session, _unique_code())

    add_prerequisite_service(db_session, c1.id, c2.id)

    with pytest.raises(DuplicatePrerequisiteError):
        add_prerequisite_service(db_session, c1.id, c2.id)


def test_list_prereqs_requires_course_exists(db_session: Session) -> None:
    with pytest.raises(PrerequisiteNotFoundError, match="Course not found"):
        list_prerequisites_service(db_session, course_id=999999)


def test_remove_prereq_not_found(db_session: Session) -> None:
    c1 = _create_course(db_session, _unique_code())
    c2 = _create_course(db_session, _unique_code())

    with pytest.raises(PrerequisiteNotFoundError, match="Prerequisite relation not found"):
        remove_prerequisite_service(db_session, c1.id, c2.id)


def test_happy_path_add_list_remove(db_session: Session) -> None:
    c1 = _create_course(db_session, _unique_code())
    c2 = _create_course(db_session, _unique_code())

    add_prerequisite_service(db_session, c1.id, c2.id)

    links = list_prerequisites_service(db_session, c1.id)
    assert any(l.prereq_course_id == c2.id for l in links)

    remove_prerequisite_service(db_session, c1.id, c2.id)

    links_after = list_prerequisites_service(db_session, c1.id)
    assert not any(l.prereq_course_id == c2.id for l in links_after)
