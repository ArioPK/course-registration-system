# backend/app/schemas/legacy_prerequisite.py

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, model_validator


class LegacyPrerequisiteRead(BaseModel):
    """
    Legacy flat prerequisite response.

    Includes BOTH key styles to support:
    - frontend legacy keys: target_course_id, prerequisite_course_id
    - backend canonical keys: course_id, prereq_course_id
    """
    model_config = ConfigDict(from_attributes=True)

    course_id: int
    prereq_course_id: int
    target_course_id: int
    prerequisite_course_id: int
    id: Optional[int] = None  # only if association table ever has a surrogate id


class LegacyPrerequisiteCreate(BaseModel):
    """
    Accept BOTH payload styles:
    - {target_course_id, prerequisite_course_id}
    - {course_id, prereq_course_id}

    Normalizes into course_id + prereq_course_id.
    """
    course_id: Optional[int] = None
    prereq_course_id: Optional[int] = None
    target_course_id: Optional[int] = None
    prerequisite_course_id: Optional[int] = None

    @model_validator(mode="after")
    def normalize_and_validate(self) -> "LegacyPrerequisiteCreate":
        if self.course_id is None and self.target_course_id is not None:
            self.course_id = self.target_course_id
        if self.prereq_course_id is None and self.prerequisite_course_id is not None:
            self.prereq_course_id = self.prerequisite_course_id

        if self.course_id is None or self.prereq_course_id is None:
            raise ValueError(
                "Missing required keys. Provide either "
                "{course_id, prereq_course_id} or {target_course_id, prerequisite_course_id}."
            )

        return self
