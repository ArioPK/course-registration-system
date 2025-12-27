# backend/app/routers/legacy_prerequisites.py

from __future__ import annotations

from typing import List, Tuple

from fastapi import APIRouter, Body, Depends, HTTPException, status, Response
from pydantic import ValidationError
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.dependencies.auth import get_current_admin
from backend.app.models.admin import Admin
from backend.app.schemas.legacy_prerequisite import (
    LegacyPrerequisiteCreate,
    LegacyPrerequisiteRead,
)
from backend.app.services.prerequisite_service import (
    add_prerequisite_service,
    list_all_prerequisites_service,
    remove_prerequisite_service,
    DuplicatePrerequisiteError,
    InvalidPrerequisiteRelationError,
    PrerequisiteNotFoundError,
)

router = APIRouter(
    prefix="/api/prerequisites",
    tags=["prerequisites-legacy"],
)


def _canonical_legacy_id(course_id: int, prereq_course_id: int) -> str:
    # Canonical format returned by GET/POST:
    # "{course_id}-{prereq_course_id}"
    return f"{course_id}-{prereq_course_id}"


def _to_legacy_read(link) -> LegacyPrerequisiteRead:
    course_id = link.course_id
    prereq_course_id = link.prereq_course_id
    return LegacyPrerequisiteRead(
        id=_canonical_legacy_id(course_id, prereq_course_id),
        course_id=course_id,
        prereq_course_id=prereq_course_id,
        target_course_id=course_id,
        prerequisite_course_id=prereq_course_id,
    )


def _parse_legacy_id(raw_id: str) -> Tuple[int, int]:
    """
    Accept:
      - "course_id-prereq_course_id" (canonical)
      - "course_id:prereq_course_id" (accepted for robustness)
    """
    if "-" in raw_id:
        parts = raw_id.split("-")
    elif ":" in raw_id:
        parts = raw_id.split(":")
    else:
        parts = []

    if len(parts) != 2:
        raise ValueError("Invalid id format")

    try:
        course_id = int(parts[0])
        prereq_course_id = int(parts[1])
    except Exception as e:
        raise ValueError("Invalid id format") from e

    if course_id <= 0 or prereq_course_id <= 0:
        raise ValueError("Invalid id format")

    return course_id, prereq_course_id


@router.get("", response_model=List[LegacyPrerequisiteRead])
def list_all_prerequisites(
    db: Session = Depends(get_db),
    _current_admin: Admin = Depends(get_current_admin),
) -> List[LegacyPrerequisiteRead]:
    links = list_all_prerequisites_service(db)
    return [_to_legacy_read(link) for link in links]


@router.post("", response_model=LegacyPrerequisiteRead, status_code=status.HTTP_201_CREATED)
def create_prerequisite(
    payload: dict = Body(...),  # manual validation to return 400 instead of FastAPI 422
    db: Session = Depends(get_db),
    _current_admin: Admin = Depends(get_current_admin),
) -> LegacyPrerequisiteRead:
    # Validate & normalize payload to internal names using Pydantic,
    # but return 400 on schema issues for frontend friendliness.
    try:
        data = LegacyPrerequisiteCreate.model_validate(payload)
    except ValidationError as e:
        # Return 400 for invalid payload shape (frontend-friendly)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.errors())

    try:
        link = add_prerequisite_service(
            db,
            course_id=data.course_id,               # type: ignore[arg-type]
            prereq_course_id=data.prereq_course_id, # type: ignore[arg-type]
        )
        return _to_legacy_read(link)

    except InvalidPrerequisiteRelationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except DuplicatePrerequisiteError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except PrerequisiteNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prerequisite_legacy(
    id: str,
    db: Session = Depends(get_db),
    _current_admin: Admin = Depends(get_current_admin),
) -> Response:
    """
    Legacy delete shim.

    Accepts id formats:
      - "{course_id}-{prereq_course_id}" (canonical)
      - "{course_id}:{prereq_course_id}" (accepted for robustness)
    """
    try:
        course_id, prereq_course_id = _parse_legacy_id(id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid id format. Expected 'course_id-prereq_course_id' or 'course_id:prereq_course_id'.",
        )

    try:
        remove_prerequisite_service(db, course_id=course_id, prereq_course_id=prereq_course_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except PrerequisiteNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidPrerequisiteRelationError as e:
        # Not typical for delete, but keep consistent mapping
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
