# backend/app/schemas/schedule.py

from datetime import time
from pydantic import BaseModel
from typing import List

class ScheduleBlockRead(BaseModel):
    course_id: int
    code: str
    name: str
    start_time: time
    end_time: time
    location: str
    professor_name: str
    units: int

class ScheduleDayRead(BaseModel):
    day_of_week: str
    blocks: List[ScheduleBlockRead]

class WeeklyScheduleRead(BaseModel):
    term: str
    days: List[ScheduleDayRead]