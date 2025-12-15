# backend/create_db.py

from backend.app.database import Base, engine

# Import models so they are registered with Base.metadata
from backend.app.models.admin import Admin  # noqa: F401
from backend.app.models.course import Course  # noqa: F401
from backend.app.models.student import Student  # noqa: F401

def main() -> None:
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")

if __name__ == "__main__":
    main()
