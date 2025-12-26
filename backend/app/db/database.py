from collections.abc import Generator

from sqlalchemy import create_engine # type: ignore
from sqlalchemy.orm import sessionmaker # type: ignore

from backend.app.config.settings import settings  


# Create the SQLAlchemy engine using the DATABASE_URL from settings
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,   # Logs SQL in debug mode; set DEBUG=false in production
    pool_pre_ping=True,    # Helps avoid stale connections
)

# Session factory for DB access
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator:
    """
    FastAPI dependency that provides a database session.

    Usage in views:
        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
