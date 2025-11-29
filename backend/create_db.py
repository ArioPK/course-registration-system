"""
Standalone script to create database tables based on SQLAlchemy models.

Usage (from project root):
    python backend/create_db.py

This script uses the DATABASE_URL from your configuration and will create
all tables defined on subclasses of Base.
"""

from app.database import Base, engine  # type: ignore[import]


def main() -> None:
    # Import models here once they exist, so they are registered with Base.
    # For example:
    #
    # from app.models import admin, course  # noqa: F401
    #
    # This ensures that Base.metadata includes all tables.
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")


if __name__ == "__main__":
    main()
