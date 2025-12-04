# backend/manual_test_course_schema.py

from datetime import time
from pydantic import ValidationError

from app.schemas.course import CourseCreate, DayOfWeek


def main() -> None:
    print("=== Valid CourseCreate example ===")
    valid_course = CourseCreate(
        code="CS101",
        name="Intro to CS",
        capacity=50,
        professor_name="Dr. Smith",
        day_of_week=DayOfWeek.MONDAY,
        start_time=time(hour=9, minute=0),
        end_time=time(hour=10, minute=30),
        location="Room 101",
    )
    print(valid_course)
    print()

    print("=== Invalid CourseCreate example (negative capacity, empty code) ===")
    try:
        CourseCreate(
            code="   ",           # invalid empty
            name="Bad Course",
            capacity=-5,          # invalid negative
            professor_name="Dr. Who",
            day_of_week=DayOfWeek.SUNDAY,
            start_time=time(hour=8, minute=0),
            end_time=time(hour=9, minute=0),
            location="Room 999",
        )
    except ValidationError as e:
        print("ValidationError raised as expected:")
        print(e.json(indent=2))


if __name__ == "__main__":
    main()
