# backend/app/routers/admin_unit_limits.py

from fastapi import APIRouter, Body, Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.dependencies.auth import get_current_admin
from backend.app.models.admin import Admin
from backend.app.schemas.unit_limits import UnitLimitRead, UnitLimitUpdate
from backend.app.services.unit_limit_service import (
    get_unit_limits_service,
    update_unit_limits_service,
    InvalidUnitLimitRangeError,
)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/unit-limits", response_model=UnitLimitRead, status_code=status.HTTP_200_OK)
def get_unit_limits(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),  # enforced admin auth
) -> UnitLimitRead:
    policy = get_unit_limits_service(db)
    return policy


@router.put("/unit-limits", response_model=UnitLimitRead, status_code=status.HTTP_200_OK)
def update_unit_limits(
    payload: dict = Body(...),  # validate manually to return 400 instead of FastAPI's 422
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),  # enforced admin auth
) -> UnitLimitRead:
    # Convert Pydantic validation errors (schema-level) into HTTP 400 for this endpoint.
    try:
        data = UnitLimitUpdate.model_validate(payload)  # Pydantic v2
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.errors(),
        )

    # Service-level validation (source of truth)
    try:
        policy = update_unit_limits_service(db, data.min_units, data.max_units)
        return policy
    except InvalidUnitLimitRangeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
