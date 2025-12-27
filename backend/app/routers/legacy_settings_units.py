# backend/app/routers/legacy_settings_units.py

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

router = APIRouter(prefix="/api/settings", tags=["settings-legacy"])


@router.get("/units", response_model=UnitLimitRead)
def get_units(
    db: Session = Depends(get_db),
    _current_admin: Admin = Depends(get_current_admin),
) -> UnitLimitRead:
    policy = get_unit_limits_service(db)
    return UnitLimitRead.model_validate(policy)


@router.put("/units", response_model=UnitLimitRead, status_code=status.HTTP_200_OK)
def update_units(
    payload: dict = Body(...),  # manual validation -> return 400 instead of FastAPI 422
    db: Session = Depends(get_db),
    _current_admin: Admin = Depends(get_current_admin),
) -> UnitLimitRead:
    try:
        data = UnitLimitUpdate.model_validate(payload)
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
        policy = update_unit_limits_service(db, data.min_units, data.max_units)
    except InvalidUnitLimitRangeError as ex:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ex))

    return UnitLimitRead.model_validate(policy)
    