# backend/tests/test_current_term_config.py

from datetime import time
import pytest

from backend.app.models.course import Course
from backend.app.models.professor import Professor
from backend.app.models.student import Student
from backend.app.repositories import enrollment_repository
from backend.app.utils.current_term import get_current_term
from backend.app.services.drop_service import drop_student_course, NotEnrolledError
from backend.app.services import professor_service
from backend.tests.test_enrollment_service import _new_id


def _make_student(db_session, *, full_name: str = "Student One") -> Student:
    i = _new_id()
    s_num = f"S{i:05d}"

    data = dict(
        student_number=s_num,
        full_name=full_name,
        email=f"{s_num}@test.local",
        password_hash="x",
        is_active=True,
    )
    if hasattr(Student, "national_id"):
        data["national_id"] = f"{i:010d}"
    if hasattr(Student, "phone_number"):
        data["phone_number"] = "09120000000"
    if hasattr(Student, "major"):
        data["major"] = "CS"
    if hasattr(Student, "entry_year"):
        data["entry_year"] = 1400
    if hasattr(Student, "units_taken"):
        data["units_taken"] = 0

    s = Student(**data)
    db_session.add(s)
    db_session.commit()
    db_session.refresh(s)
    return s


def _make_professor(db_session, *, full_name: str = "Dr. Alice Smith") -> Professor:
    i = _new_id()
    p_num = f"P{i:05d}"

    data = dict(
        full_name=full_name,
        email=f"{p_num}@test.local",
        password_hash="x",
        is_active=True,
    )
    # adapt to either professor_number or professor_code
    if hasattr(Professor, "professor_number"):
        data["professor_number"] = p_num
    elif hasattr(Professor, "professor_code"):
        data["professor_code"] = p_num

    if hasattr(Professor, "national_id"):
        data["national_id"] = f"{i:010d}"
    if hasattr(Professor, "phone_number"):
        data["phone_number"] = "09120000000"
    if hasattr(Professor, "department"):
        data["department"] = "CS"

    p = Professor(**data)
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)
    return p


def _make_course(db_session, *, code: str, professor_name: str, semester: str) -> Course:
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
    db_session.refresh(c)
    return c


def test_get_current_term_reads_env(monkeypatch):
    monkeypatch.setenv("CURRENT_TERM", "1404-2")
    assert get_current_term() == "1404-2"


def test_drop_service_scoped_to_current_term(db_session, monkeypatch):
    # Enrollment exists in 1404-1, but CURRENT_TERM is 1404-2 => drop behaves as not enrolled
    monkeypatch.setenv("CURRENT_TERM", "1404-2")

    s = _make_student(db_session)
    c = _make_course(db_session, code="CS101", professor_name="Dr. X", semester="1404-1")

    enrollment_repository.create(db_session, student_id=s.id, course_id=c.id, term="1404-1")

    with pytest.raises(NotEnrolledError):
        drop_student_course(db_session, student_id=s.id, course_id=c.id, term=None)


def test_professor_remove_student_blocks_non_current_term(db_session, monkeypatch):
    # Enrollment exists in 1404-1, but CURRENT_TERM is 1404-2 => must raise NotCurrentTermError
    monkeypatch.setenv("CURRENT_TERM", "1404-2")

    prof = _make_professor(db_session, full_name="Dr. Alice Smith")
    course = _make_course(db_session, code="CS201", professor_name=prof.full_name, semester="1404-1")
    student = _make_student(db_session)

    enrollment_repository.create(db_session, student_id=student.id, course_id=course.id, term="1404-1")

    with pytest.raises(professor_service.NotCurrentTermError):
        professor_service.professor_remove_student(
            db_session,
            professor=prof,
            course_id=course.id,
            student_id=student.id,
            term=None,
        )