# backend/app/models/professor.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func

from backend.app.database import Base


class Professor(Base):
    __tablename__ = "professors"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Login identifier
    professor_code = Column(String(50), unique=True, index=True, nullable=False)

    # Profile
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=True)

    # Auth
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Professor id={self.id} code={self.professor_code!r}>"
