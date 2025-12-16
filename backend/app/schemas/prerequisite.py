# backend/app/schemas/prerequisite.py

from typing import List

from pydantic import BaseModel, ConfigDict, model_validator


class PrerequisiteCreate(BaseModel):
    """
    Request body for adding a prerequisite relation:
    course_id -> prereq_course_id
    """
    course_id: int
    prereq_course_id: int

    @model_validator(mode="after")
    def validate_not_self_prerequisite(self) -> "PrerequisiteCreate":
        if self.course_id == self.prereq_course_id:
            raise ValueError("course_id and prereq_course_id must be different (self-prerequisite is not allowed).")
        return self


# -----------------------------
# READ SCHEMAS (choose ONE)
# -----------------------------

# Variant A (ONLY if your association table has a surrogate `id` column)
# class PrerequisiteRead(BaseModel):
#     model_config = ConfigDict(from_attributes=True)
#
#     id: int
#     course_id: int
#     prereq_course_id: int


# Variant B (RECOMMENDED for your current DB: composite key, NO `id`)
class PrerequisiteRead(BaseModel):
    """
    Response shape for reading prerequisite relations.
    Matches association tables that use (course_id, prereq_course_id) as the key.
    """
    model_config = ConfigDict(from_attributes=True)

    course_id: int
    prereq_course_id: int


class PrerequisiteListResponse(BaseModel):
    """
    Optional wrapper if you ever want a consistent envelope:
    { "items": [...] }
    Most endpoints can simply return List[PrerequisiteRead].
    """
    items: List[PrerequisiteRead]
