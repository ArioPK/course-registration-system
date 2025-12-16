# backend/tests/test_unit_limit_service.py

import pytest
from sqlalchemy.orm import Session

from backend.app.models.unit_limit_policy import UnitLimitPolicy
from backend.app.services.unit_limit_service import (
    InvalidUnitLimitRangeError,
    get_unit_limits_service,
    update_unit_limits_service,
)
from backend.app.repositories.unit_limit_repository import POLICY_ID, DEFAULT_MIN_UNITS, DEFAULT_MAX_UNITS, get_or_create_policy


def _clear_policy_table(db: Session) -> None:
    db.query(UnitLimitPolicy).delete(synchronize_session=False)
    db.commit()


def test_get_unit_limits_returns_default_if_missing(db_session: Session) -> None:
    _clear_policy_table(db_session)

    policy = get_unit_limits_service(db_session)

    assert policy.id == POLICY_ID
    assert policy.min_units == DEFAULT_MIN_UNITS
    assert policy.max_units == DEFAULT_MAX_UNITS


def test_update_unit_limits_success_persists(db_session: Session) -> None:
    _clear_policy_table(db_session)

    updated = update_unit_limits_service(db_session, 10, 25)
    assert updated.id == POLICY_ID
    assert updated.min_units == 10
    assert updated.max_units == 25

    again = get_unit_limits_service(db_session)
    assert again.min_units == 10
    assert again.max_units == 25


def test_update_rejects_negative_min(db_session: Session) -> None:
    with pytest.raises(InvalidUnitLimitRangeError, match="min_units must be >= 0"):
        update_unit_limits_service(db_session, -1, 10)


def test_update_rejects_negative_max(db_session: Session) -> None:
    with pytest.raises(InvalidUnitLimitRangeError, match="max_units must be >= 0"):
        update_unit_limits_service(db_session, 0, -5)


def test_update_rejects_min_greater_than_max(db_session: Session) -> None:
    with pytest.raises(InvalidUnitLimitRangeError, match="min_units must be <= max_units"):
        update_unit_limits_service(db_session, 20, 10)


def test_repository_get_or_create_is_idempotent(db_session: Session) -> None:
    _clear_policy_table(db_session)

    p1 = get_or_create_policy(db_session)
    p2 = get_or_create_policy(db_session)

    assert p1.id == POLICY_ID
    assert p2.id == POLICY_ID

    count = db_session.query(UnitLimitPolicy).count()
    assert count == 1
