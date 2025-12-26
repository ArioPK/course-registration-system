from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.sql import func

from backend.app.database import Base  


class Admin(Base):
    __tablename__ = "admins"

    id: int = Column(Integer, primary_key=True, index=True)
    username: str = Column(String(50), unique=True, index=True, nullable=False)
    national_id: str = Column(String(20), unique=True, index=True, nullable=False)
    email: str = Column(String(255), unique=True, index=True, nullable=False)
    password_hash: str = Column(String(255), nullable=False)

    is_active: bool = Column(Boolean, nullable=False, default=True)

    created_at: datetime = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: datetime = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    #helps when debugging 
    def __repr__(self) -> str:
        return (
            f"<Admin id={self.id!r} "
            f"username={self.username!r} "
            f"email={self.email!r} "
            f"is_active={self.is_active!r}>"
        )
