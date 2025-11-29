from collections.abc import Generator

from sqlalchemy import create_engine # type: ignore
from sqlalchemy.orm import sessionmaker, declarative_base, Session # type: ignore

from .config.settings import settings  # relative import from app.config


# SQLAlchemy Base class for ORM models to inherit from
Base = declarative_base()

# SQLAlchemy engine: core connection to the database
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,   # If True, logs all SQL statements (useful in dev)
    pool_pre_ping=True,    # Checks connections before using them (avoids stale connections)
    future=True,           # Use SQLAlchemy 2.0 style behavior
)

# Session factory: creates new Session objects bound to our engine
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=Session,        # Explicit Session class (optional but clear)
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session per request.

    Usage in an endpoint:
        def endpoint(db: Session = Depends(get_db)):
            ...

    The session is created, yielded to the endpoint, and then closed.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
