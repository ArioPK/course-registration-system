# backend/app/services/unit_limit_service.py

from sqlalchemy.orm import Session

from backend.app.models.unit_limit_policy import UnitLimitPolicy
from backend.app.repositories.unit_limit_repository import (
    DEFAULT_MAX_UNITS,
    DEFAULT_MIN_UNITS,
    get_or_create_policy,
    set_policy,
)


class InvalidUnitLimitRangeError(Exception):
    """Raised when min/max values violate unit policy rules."""


def _validate_unit_limits(min_units: int, max_units: int) -> None:
    if min_units < 0:
        raise InvalidUnitLimitRangeError("min_units must be >= 0.")
    if max_units < 0:
        raise InvalidUnitLimitRangeError("max_units must be >= 0.")
    if min_units > max_units:
        raise InvalidUnitLimitRangeError("min_units must be <= max_units.")


def get_unit_limits_service(db: Session) -> UnitLimitPolicy:
    """
    Returns the current unit limit policy.
    If missing, creates the default singleton policy row (id=1).
    """
    return get_or_create_policy(db, default_min=DEFAULT_MIN_UNITS, default_max=DEFAULT_MAX_UNITS)


def update_unit_limits_service(db: Session, min_units: int, max_units: int) -> UnitLimitPolicy:
    """
    Validates and persists the unit limit policy update.
    """
    _validate_unit_limits(min_units, max_units)
    return set_policy(db, min_units=min_units, max_units=max_units)
