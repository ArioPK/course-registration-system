# backend/tests/test_unit_limit_policy.py

import pytest
from sqlalchemy.orm import Session

from backend.app.models.unit_limit_policy import UnitLimitPolicy
from backend.seed_unit_limit_policy import ensure_unit_limit_policy


def test_seed_creates_singleton_row(db_session: Session) -> None:
    assert db_session.get(UnitLimitPolicy, 1) is None

    policy = ensure_unit_limit_policy(db_session, min_units=0, max_units=30)
    assert policy.id == 1
    assert policy.min_units == 0
    assert policy.max_units == 30

    # second run is idempotent (no duplicates)
    policy2 = ensure_unit_limit_policy(db_session, min_units=0, max_units=30)
    assert policy2.id == 1

    count = db_session.query(UnitLimitPolicy).count()
    assert count == 1


def test_seed_rejects_invalid_values(db_session: Session) -> None:
    with pytest.raises(ValueError):
        ensure_unit_limit_policy(db_session, min_units=-1, max_units=30)

    with pytest.raises(ValueError):
        ensure_unit_limit_policy(db_session, min_units=10, max_units=5)
