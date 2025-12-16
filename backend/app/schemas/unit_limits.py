# backend/app/schemas/unit_limits.py

from pydantic import BaseModel, ConfigDict, model_validator


class UnitLimitRead(BaseModel):
    """
    Read model for unit limit policy.
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    min_units: int
    max_units: int


class UnitLimitUpdate(BaseModel):
    """
    Update model for unit limit policy.
    Validation here is helpful for future API endpoints, but
    service-layer validation remains the source of truth.
    """
    min_units: int
    max_units: int

    @model_validator(mode="after")
    def validate_range(self) -> "UnitLimitUpdate":
        if self.min_units < 0:
            raise ValueError("min_units must be >= 0.")
        if self.max_units < 0:
            raise ValueError("max_units must be >= 0.")
        if self.min_units > self.max_units:
            raise ValueError("min_units must be <= max_units.")
        return self
