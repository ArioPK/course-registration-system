# backend/app/routers/course.py

from __future__ import annotations

from typing import Any, List

from fastapi import APIRouter, Depends # type: ignore
from sqlalchemy.orm import Session # type: ignore

from ..database import get_db
from ..dependencies.auth import get_current_admin
from ..models.admin import Admin
from ..models.course import Course

router = APIRouter(
    prefix="/courses",
    tags=["courses"],
)


@router.get("/", response_model=List[Any])  # replace with proper schema later
async def list_courses(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> Any:
    """
    Example protected endpoint.

    Only accessible if the request includes a valid Bearer token
    for an existing admin. The get_current_admin dependency enforces this.
    """

    courses = db.query(Course).all()
    # TODO: map to Pydantic response models
    return [
        {
            "id": c.id,
            "code": c.code,
            "name": c.name,
        }
        for c in courses
    ]
