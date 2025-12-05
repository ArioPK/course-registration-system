# backend/tests/conftest.py

import os
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from backend.app.database import Base, get_db
from backend.app.main import app


# 1. Test database URL & engine

# Use a separate SQLite database file for tests.
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///./test.db")

# For SQLite, we need check_same_thread=False so multiple sessions can be used.
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False} if TEST_DATABASE_URL.startswith("sqlite") else {},
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


# 2. Create/drop tables for the test database

@pytest.fixture(scope="session", autouse=True)
def prepare_test_database() -> Generator[None, None, None]:
    """
    Create all tables in the test database at the start of the test session,
    and drop them at the end.

    This ensures tests use a clean schema that is completely separate
    from the main application's database.
    """
    Base.metadata.create_all(bind=test_engine)
    try:
        yield
    finally:
        Base.metadata.drop_all(bind=test_engine)


# 3. Per-test DB session fixture

@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    """
    Provides a fresh SQLAlchemy session for each test.

    This session is bound to the test engine and is independent of the
    application's main SessionLocal. Tests can use this fixture directly
    to insert/query data in the test DB.
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


# 4. FastAPI TestClient fixture with get_db override

@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    """
    Provides a FastAPI TestClient that uses the test database.

    It overrides the application's get_db dependency to inject sessions
    from the test engine instead of the real database.
    """

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.rollback()
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    # Clean up overrides after the test
    app.dependency_overrides.clear()
