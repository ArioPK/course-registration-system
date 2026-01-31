# backend/tests/conftest.py

import os
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session

from backend.app.database import Base, get_db
from backend.app.main import app
from backend.tests import factories
from backend.tests.factories import CURRENT_TERM 


TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///./test.db")

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False} if TEST_DATABASE_URL.startswith("sqlite") else {},
)

@pytest.fixture()
def current_term(monkeypatch):
    """
    Fixture to set the current term for tests.
    """
    monkeypatch.setenv("CURRENT_TERM", CURRENT_TERM)
    return CURRENT_TERM

@pytest.fixture(scope="session", autouse=True)
def prepare_test_database() -> Generator[None, None, None]:
    Base.metadata.create_all(bind=test_engine)
    try:
        yield
    finally:
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    """
    Per-test DB session that is isolated via an outer transaction + SAVEPOINT.
    This prevents committed data from leaking between tests.
    """
    connection = test_engine.connect()
    transaction = connection.begin()

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    db = TestingSessionLocal()

    # Start a nested transaction (SAVEPOINT) so test code can commit safely.
    db.begin_nested()

    @event.listens_for(db, "after_transaction_end")
    def _restart_savepoint(session, trans):
        # Re-open SAVEPOINT after each commit/rollback inside the test
        if trans.nested and not trans._parent.nested:
            session.begin_nested()

    try:
        yield db
    finally:
        db.close()

        # Some tests may rollback/close the outer transaction already (e.g., after IntegrityError).
        if transaction.is_active:
            transaction.rollback()

        connection.close()

@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """
    TestClient that uses the SAME db_session as the test (same transaction),
    so API calls see the test data and nothing leaks across tests.
    """
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()