# backend/tests/factories.py

from __future__ import annotations

from datetime import datetime, time
from itertools import count
from typing import Any

from sqlalchemy.orm import Session

from backend.app.models.course import Course
from backend.app.models.professor import Professor
from backend.app.models.student import Student
from backend.app.repositories import enrollment_repository
import uuid

CURRENT_TERM = "1404-1"

_seq = count(int(uuid.uuid4().int % 900000) + 100000)  # start 100000..999999


def _unique_digits(n: int = 10) -> str:
    # 10 digits string, unique enough for tests
    return str(int(uuid.uuid4().int % (10**n))).zfill(n)


def _next_i() -> int:
    return next(_seq)


def _parse_time(v: str | time) -> time:
    if isinstance(v, time):
        return v
    s = v.strip()
    fmt = "%H:%M:%S" if len(s.split(":")) == 3 else "%H:%M"
    return datetime.strptime(s, fmt).time()


def _persist(db: Session, obj):
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def make_student(
    db: Session,
    *,
    full_name: str = "Test Student",
    student_number: str | None = None,
    email: str | None = None,
    password: str = "x",
    **overrides: Any,
) -> Student:
    _ = _next_i()
    s_num = student_number or f"S{_unique_digits(10)}"

    data: dict[str, Any] = {}

    # Identifier field name can vary by project; support common variants.
    if hasattr(Student, "student_number"):
        data["student_number"] = s_num
    elif hasattr(Student, "student_code"):
        data["student_code"] = s_num
    else:
        raise ValueError("Student model missing student_number/student_code")

    data["full_name"] = full_name

    if hasattr(Student, "email"):
        data["email"] = email or f"{s_num}@test.local"

    # Fill common NOT NULL fields if they exist
    if hasattr(Student, "national_id"):
        data["national_id"] = overrides.pop("national_id", _unique_digits(10))
    if hasattr(Student, "phone_number"):
        data["phone_number"] = "09120000000"
    if hasattr(Student, "major"):
        data["major"] = "CS"
    if hasattr(Student, "entry_year"):
        data["entry_year"] = 1400
    if hasattr(Student, "units_taken"):
        data["units_taken"] = 0
    if hasattr(Student, "is_active"):
        data["is_active"] = True

    # Password field naming differs across projects
    if hasattr(Student, "password_hash"):
        data["password_hash"] = password
    elif hasattr(Student, "password"):
        data["password"] = password

    data.update(overrides)
    return _persist(db, Student(**data))


def make_professor(
    db: Session,
    *,
    full_name: str = "Test Professor",
    professor_number: str | None = None,
    email: str | None = None,
    password: str = "x",
    **overrides: Any,
) -> Professor:
    i = _next_i()
    p_num = professor_number or f"P{i:05d}"

    data: dict[str, Any] = {}

    # Identifier field name can vary; support common variants.
    if hasattr(Professor, "professor_number"):
        data["professor_number"] = p_num
    elif hasattr(Professor, "professor_code"):
        data["professor_code"] = p_num
    else:
        raise ValueError("Professor model missing professor_number/professor_code")

    data["full_name"] = full_name

    if hasattr(Professor, "email"):
        data["email"] = email or f"{p_num}@test.local"

    if hasattr(Professor, "national_id"):
        data["national_id"] = overrides.pop("national_id", _unique_digits(10))
    if hasattr(Professor, "phone_number"):
        data["phone_number"] = "09120000000"
    if hasattr(Professor, "department"):
        data["department"] = "CS"
    if hasattr(Professor, "is_active"):
        data["is_active"] = True

    if hasattr(Professor, "password_hash"):
        data["password_hash"] = password
    elif hasattr(Professor, "password"):
        data["password"] = password

    data.update(overrides)
    return _persist(db, Professor(**data))


def make_course(
    db: Session,
    *,
    code: str | None = None,
    name: str | None = None,
    semester: str = CURRENT_TERM,
    units: int = 3,
    capacity: int = 30,
    day_of_week: str = "MON",
    start_time: str | time = "09:00",
    end_time: str | time = "10:00",
    location: str = "Room 1",
    professor_name: str = "Test Professor",
    department: str = "CS",
    is_active: bool = True,
    **overrides: Any,
) -> Course:
    i = _next_i()
    c_code = code or f"CS{i:03d}"

    data: dict[str, Any] = {
        "code": c_code,
        "name": name or f"Course {c_code}",
        "capacity": capacity,
        "professor_name": professor_name,
        "day_of_week": day_of_week,
        "start_time": _parse_time(start_time),
        "end_time": _parse_time(end_time),
        "location": location,
        "is_active": is_active,
        "units": units,
    }

    # Term/semester field name can vary
    if hasattr(Course, "semester"):
        data["semester"] = semester
    elif hasattr(Course, "term"):
        data["term"] = semester
    else:
        # keep default "semester" if your model uses it but hasattr check failed
        data["semester"] = semester

    # Department field can vary; cover common variants
    if hasattr(Course, "department"):
        data["department"] = department
    elif hasattr(Course, "department_name"):
        data["department_name"] = department
    elif hasattr(Course, "dept"):
        data["dept"] = department

    data.update(overrides)
    return _persist(db, Course(**data))


def add_enrollment(
    db: Session,
    *,
    student_id: int,
    course_id: int,
    term: str = CURRENT_TERM,
):
    e = enrollment_repository.create(db, student_id=student_id, course_id=course_id, term=term)
    if e is None:
        e = enrollment_repository.get_by_student_course_term(db, student_id, course_id, term)
    if e is None:
        raise RuntimeError("Enrollment repository did not create or return enrollment")
    try:
        db.refresh(e)
    except Exception:
        pass
    return e


def add_prerequisite(db: Session, *, course_id: int, prereq_course_id: int):
    # Keep imports local to avoid accidental use outside tests.
    try:
        from backend.app.models.course_prerequisite import CoursePrerequisite  # type: ignore
    except Exception:  # pragma: no cover
        from backend.app.models.prerequisite import CoursePrerequisite  # type: ignore

    data: dict[str, Any] = {"course_id": course_id}

    # Common field names
    if hasattr(CoursePrerequisite, "prerequisite_course_id"):
        data["prerequisite_course_id"] = prereq_course_id
    elif hasattr(CoursePrerequisite, "prereq_course_id"):
        data["prereq_course_id"] = prereq_course_id
    else:
        raise ValueError("CoursePrerequisite missing prerequisite_course_id/prereq_course_id")

    return _persist(db, CoursePrerequisite(**data))


def add_history(
    db: Session,
    *,
    student_id: int,
    course_id: int,
    term: str = CURRENT_TERM,
    status: str = "passed",
    grade: Any | None = None,
):
    try:
        from backend.app.models.student_course_history import StudentCourseHistory  # type: ignore
    except Exception:  # pragma: no cover
        from backend.app.models.history import StudentCourseHistory  # type: ignore

    data: dict[str, Any] = {
        "student_id": student_id,
        "course_id": course_id,
    }

    # term field name can vary
    if hasattr(StudentCourseHistory, "term"):
        data["term"] = term
    elif hasattr(StudentCourseHistory, "semester"):
        data["semester"] = term

    if hasattr(StudentCourseHistory, "status"):
        data["status"] = status
    if grade is not None and hasattr(StudentCourseHistory, "grade"):
        data["grade"] = grade

    return _persist(db, StudentCourseHistory(**data))


def set_unit_policy(db: Session, *, min_units: int = 0, max_units: int = 20):
    try:
        from backend.app.models.unit_limit_policy import UnitLimitPolicy  # type: ignore
    except Exception:  # pragma: no cover
        from backend.app.models.policy import UnitLimitPolicy  # type: ignore

    data: dict[str, Any] = {}

    if hasattr(UnitLimitPolicy, "min_units"):
        data["min_units"] = min_units
    if hasattr(UnitLimitPolicy, "max_units"):
        data["max_units"] = max_units

    return _persist(db, UnitLimitPolicy(**data))


def make_admin(
    db: Session,
    *,
    username: str = "admin",
    password: str = "x",
    **overrides: Any,
):
    # Optional: only if your project has an Admin model. Keep it safe and test-only.
    try:
        from backend.app.models.admin import Admin  # type: ignore
    except Exception:  # pragma: no cover
        raise RuntimeError("Admin model not found in backend.app.models.admin")

    data: dict[str, Any] = {}

    if hasattr(Admin, "username"):
        data["username"] = username
    elif hasattr(Admin, "admin_username"):
        data["admin_username"] = username
    else:
        raise ValueError("Admin model missing username/admin_username")

    if hasattr(Admin, "password_hash"):
        data["password_hash"] = password
    elif hasattr(Admin, "password"):
        data["password"] = password

    if hasattr(Admin, "is_active"):
        data["is_active"] = True

    data.update(overrides)
    return _persist(db, Admin(**data))