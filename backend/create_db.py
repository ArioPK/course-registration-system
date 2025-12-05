
from backend.app.database import Base, engine  # type: ignore[import]
from backend.app.models import admin  # noqa: F401  # ensure Admin model is imported
from backend.app.models import course  # noqa: F401  # ensure Course model is imported

def init_db() -> None:
    """
    Initialize the database by creating all tables defined on Base subclasses.
    """
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully.")


if __name__ == "__main__":
    init_db()
