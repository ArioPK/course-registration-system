
from app.database import Base, engine  # type: ignore[import]
from app.models import admin  # noqa: F401  # ensure Admin model is imported


def init_db() -> None:
    """
    Initialize the database by creating all tables defined on Base subclasses.
    """
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully.")


if __name__ == "__main__":
    init_db()
