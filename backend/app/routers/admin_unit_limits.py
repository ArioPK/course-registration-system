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
from backend.app.utils.payload_normalization import normalize_unit_limits_payload

router = APIRouter(prefix="/api/admin", tags=["admin"])


def _safe_pydantic_errors(e: ValidationError):
    """Make pydantic v2 errors JSON-serializable (strip ctx / error objects)."""
    safe = []
    for err in e.errors():
        safe.append(
            {
                "loc": err.get("loc"),
                "msg": err.get("msg"),
                "type": err.get("type"),
            }
        )
    return safe


@router.get("/unit-limits", response_model=UnitLimitRead)
def get_unit_limits(
    db: Session = Depends(get_db),
    _current_admin: Admin = Depends(get_current_admin),
) -> UnitLimitRead:
    policy = get_unit_limits_service(db)
    if hasattr(UnitLimitRead, "model_validate"):  # pydantic v2
        return UnitLimitRead.model_validate(policy)
    return UnitLimitRead.from_orm(policy)  # pydantic v1


@router.put("/unit-limits", response_model=UnitLimitRead, status_code=status.HTTP_200_OK)
def update_unit_limits(
    payload: dict = Body(...),  # manual validation -> 400 instead of 422
    db: Session = Depends(get_db),
    _current_admin: Admin = Depends(get_current_admin),
) -> UnitLimitRead:
    normalized = normalize_unit_limits_payload(payload)

    if "min_units" not in normalized or "max_units" not in normalized:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required keys. Provide either {min_units,max_units} or {minUnits,maxUnits}.",
        )

    # Validate types / basic constraints (also handles min<=max if model enforces it)
    try:
        if hasattr(UnitLimitUpdate, "model_validate"):  # pydantic v2
            data = UnitLimitUpdate.model_validate(normalized)
        else:  # pydantic v1
            data = UnitLimitUpdate.parse_obj(normalized)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=_safe_pydantic_errors(e))

    # Domain validation in service (range rules etc.)
    try:
        policy = update_unit_limits_service(db, data.min_units, data.max_units)
    except InvalidUnitLimitRangeError as ex:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ex))

    if hasattr(UnitLimitRead, "model_validate"):
        return UnitLimitRead.model_validate(policy)
    return UnitLimitRead.from_orm(policy)
