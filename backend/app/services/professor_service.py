# backend/app/services/professor_service.py

from __future__ import annotations

from typing import Optional, List

from sqlalchemy.orm import Session

from backend.app.models.course import Course
from backend.app.utils.current_term import get_current_term


def _normalize_name(value: str | None) -> str:
    # Collapse internal whitespace + trim + casefold/lower
    return " ".join((value or "").split()).strip().lower()


def list_professor_courses(
    db: Session,
    *,
    professor,
    term: Optional[str] = None,
) -> List[Course]:
    """
    P0 mapping strategy:
    - Match Course.professor_name to Professor.full_name (normalized: collapsed whitespace, trimmed, lowercased)
    - Filter to current term (Course.semester)
    - Return stable ordering (code asc if present, then id asc)
    """
    current_term = term or get_current_term()

    prof_full_name = getattr(professor, "full_name", None)
    prof_norm = _normalize_name(prof_full_name)

    # Scope to current term in DB; ownership match in Python for robust whitespace normalization.
    courses_in_term = db.query(Course).filter(Course.semester == current_term).all()

    owned = [c for c in courses_in_term if _normalize_name(getattr(c, "professor_name", None)) == prof_norm]

    # Stable sort
    if hasattr(Course, "code"):
        owned.sort(key=lambda c: ((c.code or ""), c.id))
    else:
        owned.sort(key=lambda c: c.id)

    return owned