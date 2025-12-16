# backend/app/repositories/unit_limit_repository.py

from __future__ import annotations

from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.models.unit_limit_policy import UnitLimitPolicy

DEFAULT_MIN_UNITS = 0
DEFAULT_MAX_UNITS = 20
POLICY_ID = 1


def get_policy(db: Session) -> Optional[UnitLimitPolicy]:
    """
    Fetch the singleton policy row. Returns None if missing.
    """
    return db.query(UnitLimitPolicy).filter(UnitLimitPolicy.id == POLICY_ID).first()


def get_or_create_policy(
    db: Session,
    default_min: int = DEFAULT_MIN_UNITS,
    default_max: int = DEFAULT_MAX_UNITS,
) -> UnitLimitPolicy:
    """
    Ensures the singleton policy row exists (id=1).
    Safe to call multiple times (idempotent).
    """
    policy = get_policy(db)
    if policy:
        return policy

    policy = UnitLimitPolicy(id=POLICY_ID, min_units=default_min, max_units=default_max)
    db.add(policy)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # Race-safe fallback if another process created it.
        policy = get_policy(db)
        if policy:
            return policy
        raise
    db.refresh(policy)
    return policy


def set_policy(db: Session, min_units: int, max_units: int) -> UnitLimitPolicy:
    """
    Updates the singleton policy row (creates it if missing).
    Repository does not enforce business rules; service must validate first.
    """
    policy = get_or_create_policy(db)
    policy.min_units = min_units
    policy.max_units = max_units

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise

    db.refresh(policy)
    return policy
