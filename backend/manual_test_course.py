# backend/manual_test_course.py

"""
Manual sanity test for the Course ORM model.

Steps:
1. python backend/create_db.py
2. python backend/manual_test_course.py
"""

from datetime import time
from app.database import SessionLocal
from app.models.course import Course


def main() -> None:
    db = SessionLocal()
    try:
        # 1. Create a new Course instance
        new_course = Course(
            code="CS101",
            name="Introduction to Computer Science",
            capacity=30,
            professor_name="Dr. Smith",
            day_of_week="SAT",
            start_time=time(9, 0),
            end_time=time(11, 0),
            location="Room 101",
        )

        db.add(new_course)
        db.commit()
        db.refresh(new_course)

        print("Inserted course:", new_course)

        # 2. Query it back
        fetched = db.query(Course).filter_by(code="CS101").first()
        print("Fetched course:", fetched)

        if fetched is None:
            print("❌ Course was not found in the database.")
        else:
            print("✅ Course insert + query test passed.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
