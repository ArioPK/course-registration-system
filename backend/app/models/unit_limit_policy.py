# backend/app/models/unit_limit_policy.py

from sqlalchemy import CheckConstraint, Column, DateTime, Integer
from sqlalchemy.sql import func

from backend.app.database import Base


class UnitLimitPolicy(Base):
    """
    Stores the global min/max unit limits for enrollments.
    Single-row policy: we will use id=1 as the canonical policy row.
    """

    __tablename__ = "unit_limit_policies"

    id = Column(Integer, primary_key=True, index=True)
    min_units = Column(Integer, nullable=False, default=0)
    max_units = Column(Integer, nullable=False, default=30)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint("min_units >= 0", name="ck_unit_policy_min_nonnegative"),
        CheckConstraint("max_units >= min_units", name="ck_unit_policy_max_ge_min"),
    )

    def __repr__(self) -> str:
        return f"<UnitLimitPolicy id={self.id} min_units={self.min_units} max_units={self.max_units}>"
