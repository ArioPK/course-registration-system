# backend/app/routers/legacy_prerequisites.py

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Body, Depends, HTTPException, status
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
    DuplicatePrerequisiteError,
    InvalidPrerequisiteRelationError,
    PrerequisiteNotFoundError,
)

router = APIRouter(
    prefix="/api/prerequisites",
    tags=["prerequisites-legacy"],
)


def _to_legacy_read(link) -> LegacyPrerequisiteRead:
    course_id = link.course_id
    prereq_course_id = link.prereq_course_id
    return LegacyPrerequisiteRead(
        id=getattr(link, "id", None),
        course_id=course_id,
        prereq_course_id=prereq_course_id,
        target_course_id=course_id,
        prerequisite_course_id=prereq_course_id,
    )


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
        safe_errors = []
        for err in e.errors():
            safe_errors.append(
                {
                    "loc": err.get("loc"),
                    "msg": err.get("msg"),
                    "type": err.get("type"),
                }
            )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=safe_errors)

    try:
        link = add_prerequisite_service(
            db,
            course_id=data.course_id,           # type: ignore[arg-type]
            prereq_course_id=data.prereq_course_id,  # type: ignore[arg-type]
        )
        return _to_legacy_read(link)

    except InvalidPrerequisiteRelationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except DuplicatePrerequisiteError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except PrerequisiteNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
