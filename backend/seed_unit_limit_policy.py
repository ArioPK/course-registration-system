# backend/seed_unit_limit_policy.py

import os

from sqlalchemy.orm import Session

from backend.app.database import SessionLocal
from backend.app.models.unit_limit_policy import UnitLimitPolicy

DEFAULT_POLICY_ID = 1


def ensure_unit_limit_policy(
    db: Session,
    *,
    policy_id: int = DEFAULT_POLICY_ID,
    min_units: int = 0,
    max_units: int = 30,
) -> UnitLimitPolicy:
    """
    Ensure the singleton UnitLimitPolicy row exists.
    Uses a fixed id (default 1) to keep the policy single-row and deterministic.

    Idempotent: safe to run multiple times.
    """
    if min_units < 0:
        raise ValueError("min_units must be >= 0")
    if max_units < min_units:
        raise ValueError("max_units must be >= min_units")

    policy = db.get(UnitLimitPolicy, policy_id)
    if policy:
        return policy

    policy = UnitLimitPolicy(id=policy_id, min_units=min_units, max_units=max_units)
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return policy


def main() -> None:
    default_min = int(os.getenv("DEFAULT_MIN_UNITS", "0"))
    default_max = int(os.getenv("DEFAULT_MAX_UNITS", "30"))

    db = SessionLocal()
    try:
        policy = ensure_unit_limit_policy(db, min_units=default_min, max_units=default_max)
        print(f"✅ UnitLimitPolicy ensured: {policy}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
