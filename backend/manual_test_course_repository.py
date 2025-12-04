# backend/manual_test_course_repository.py

from datetime import time

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.schemas.course import CourseCreate, CourseUpdate, DayOfWeek
from app.repositories.course_repository import (
    get_course_by_id,
    get_courses,
    get_course_by_code,
    create_course,
    update_course,
    delete_course,
)


def main() -> None:
    # Use a real DB session (make sure create_db.py has run and 'courses' table exists)
    db: Session = SessionLocal()

    try:
        print("=== Creating a new course ===")
        course_in = CourseCreate(
            code="CS101-REPO",
            name="Repository Test Course",
            capacity=30,
            professor_name="Dr. Repo",
            day_of_week=DayOfWeek.MONDAY,
            start_time=time(hour=9, minute=0),
            end_time=time(hour=10, minute=30),
            location="Room 201",
        )

        created = create_course(db, course_in)
        print("Created course:", created.id, created.code, created.name)

        print("\n=== Fetching by ID ===")
        fetched = get_course_by_id(db, created.id)
        print("Fetched by id:", fetched.id, fetched.code, fetched.name)

        print("\n=== Fetching by code ===")
        fetched_by_code = get_course_by_code(db, "CS101-REPO")
        print("Fetched by code:", fetched_by_code.id, fetched_by_code.code)

        print("\n=== Listing courses (first 5) ===")
        courses = get_courses(db, skip=0, limit=5)
        for c in courses:
            print("-", c.id, c.code, c.name)

        print("\n=== Updating the course name and capacity ===")
        update_in = CourseUpdate(
            name="Updated Repository Test Course",
            capacity=40,
        )
        updated = update_course(db, fetched, update_in)
        print("Updated course:", updated.id, updated.code, updated.name, updated.capacity)

        print("\n=== Deleting the course ===")
        delete_course(db, updated)
        deleted = get_course_by_id(db, updated.id)
        print("After delete, get_course_by_id returns:", deleted)

        print("\n✅ Course repository manual test finished without exceptions.")

    finally:
        db.close()


if __name__ == "__main__":
    main()
