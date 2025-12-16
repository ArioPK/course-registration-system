# backend/tests/test_prerequisite_repository.py

import uuid
from datetime import time  

import pytest
from sqlalchemy.orm import Session

from backend.app.models.course import Course
from backend.app.repositories.prerequisite_repository import (
    add_prereq,
    get_prereqs_for_course,
    remove_prereq,
    DuplicatePrerequisiteError,
)


def _unique_code(prefix: str = "CS") -> str:
    return f"{prefix}{uuid.uuid4().hex[:6].upper()}"


def _create_course(db: Session, code: str) -> Course:
    course = Course(
        code=code,
        name=f"Test Course {code}",
        capacity=30,
        professor_name="Dr. Test",
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


def test_add_get_remove_prereq_flow(db_session: Session) -> None:
    c1 = _create_course(db_session, _unique_code())
    c2 = _create_course(db_session, _unique_code())

    link = add_prereq(db_session, c1.id, c2.id)
    assert link.course_id == c1.id
    assert link.prereq_course_id == c2.id

    prereqs = get_prereqs_for_course(db_session, c1.id)
    assert any(p.prereq_course_id == c2.id for p in prereqs)

    deleted = remove_prereq(db_session, c1.id, c2.id)
    assert deleted is True

    deleted_again = remove_prereq(db_session, c1.id, c2.id)
    assert deleted_again is False


def test_add_prereq_rejects_duplicate(db_session: Session) -> None:
    c1 = _create_course(db_session, _unique_code())
    c2 = _create_course(db_session, _unique_code())

    add_prereq(db_session, c1.id, c2.id)

    with pytest.raises(DuplicatePrerequisiteError):
        add_prereq(db_session, c1.id, c2.id)


def test_add_prereq_rejects_self_prerequisite(db_session: Session) -> None:
    c1 = _create_course(db_session, _unique_code())

    with pytest.raises(ValueError):
        add_prereq(db_session, c1.id, c1.id)
