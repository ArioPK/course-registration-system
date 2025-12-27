# backend/tests/test_list_all_prerequisites_service.py

from datetime import time
from typing import List, Tuple

from sqlalchemy.orm import Session

from backend.app.models.course import Course
from backend.app.models.course_prerequisite import CoursePrerequisite
from backend.app.services.prerequisite_service import list_all_prerequisites_service


def _create_course(db: Session, code: str) -> Course:
    course = Course(
        code=code,
        name=f"Course {code}",
        capacity=30,
        professor_name="Dr. Test",
        day_of_week="MON",
        start_time=time(9, 0),
        end_time=time(10, 30),
        location="Room 101",
        is_active=True,
        units=3,
        department="CS",
        semester="2025-1",
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


def test_list_all_prerequisites_returns_empty_list_when_none(db_session: Session) -> None:
    # Ensure isolation (in case DB is shared across tests)
    db_session.query(CoursePrerequisite).delete()
    db_session.commit()

    result = list_all_prerequisites_service(db_session)
    assert result == []


def test_list_all_prerequisites_returns_all_relations(db_session: Session) -> None:
    # Ensure isolation
    db_session.query(CoursePrerequisite).delete()
    db_session.commit()

    c1 = _create_course(db_session, "C101")
    c2 = _create_course(db_session, "C102")
    c3 = _create_course(db_session, "C103")

    # Create 2 relations (c3 requires c1 and c2)
    link1 = CoursePrerequisite(course_id=c3.id, prereq_course_id=c1.id)
    link2 = CoursePrerequisite(course_id=c3.id, prereq_course_id=c2.id)
    db_session.add_all([link2, link1])  # insert in reverse order on purpose
    db_session.commit()

    result = list_all_prerequisites_service(db_session)

    # Assert pairs only (composite PK)
    pairs: List[Tuple[int, int]] = [(x.course_id, x.prereq_course_id) for x in result]
    expected = sorted([(c3.id, c1.id), (c3.id, c2.id)])

    # If repository uses stable ordering, pairs should already match expected.
    assert pairs == expected
