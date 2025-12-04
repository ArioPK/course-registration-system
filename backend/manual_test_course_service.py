# backend/manual_test_course_service.py

from datetime import time

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.schemas.course import CourseCreate, CourseUpdate, DayOfWeek
from app.services.course_service import (
    create_course_service,
    list_courses_service,
    get_course_service,
    update_course_service,
    delete_course_service,
    CourseNotFoundError,
    DuplicateCourseCodeError,
)


def main() -> None:
    db: Session = SessionLocal()

    try:
        print("=== Creating a new course via service ===")
        course_in = CourseCreate(
            code="CS-SERVICE-101",
            name="Service Layer Test Course",
            capacity=25,
            professor_name="Dr. Service",
            day_of_week=DayOfWeek.SATURDAY,
            start_time=time(hour=10, minute=0),
            end_time=time(hour=11, minute=30),
            location="Service Room 1",
        )

        course = create_course_service(db=db, course_in=course_in)
        print("Created course:", course.id, course.code, course.name)

        print("\n=== Trying to create duplicate course (should raise DuplicateCourseCodeError) ===")
        try:
            create_course_service(db=db, course_in=course_in)
        except DuplicateCourseCodeError as exc:
            print("Caught expected DuplicateCourseCodeError:", exc)

        print("\n=== Listing courses ===")
        courses = list_courses_service(db=db, skip=0, limit=10)
        for c in courses:
            print("-", c.id, c.code, c.name)

        print("\n=== Updating course via service ===")
        update_in = CourseUpdate(
            name="Updated Service Layer Test Course",
            capacity=30,
        )
        updated = update_course_service(db=db, course_id=course.id, course_in=update_in)
        print("Updated course:", updated.id, updated.code, updated.name, updated.capacity)

        print("\n=== Deleting course via service ===")
        delete_course_service(db=db, course_id=course.id)

        print("\n=== Confirming course is deleted (should raise CourseNotFoundError) ===")
        try:
            get_course_service(db=db, course_id=course.id)
        except CourseNotFoundError as exc:
            print("Caught expected CourseNotFoundError:", exc)

        print("\n✅ Course service manual test finished successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    main()
