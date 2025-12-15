# backend/seed_initial_student.py

import os

from backend.app.database import SessionLocal
from backend.app.models.student import Student
from backend.app.services.security import get_password_hash


def main() -> None:
    # Dev defaults (override via env if you want)
    student_number = os.getenv("SEED_STUDENT_NUMBER", "stu_1001")
    password = os.getenv("SEED_STUDENT_PASSWORD", "password123")
    full_name = os.getenv("SEED_STUDENT_FULL_NAME", "Test Student")
    email = os.getenv("SEED_STUDENT_EMAIL", "student_test@example.com")
    national_id = os.getenv("SEED_STUDENT_NATIONAL_ID", "9876543210")
    phone_number = os.getenv("SEED_STUDENT_PHONE", "09120000000")
    major = os.getenv("SEED_STUDENT_MAJOR", "Computer Engineering")
    entry_year = int(os.getenv("SEED_STUDENT_ENTRY_YEAR", "2023"))

    db = SessionLocal()
    try:
        existing = (
            db.query(Student)
            .filter(Student.student_number == student_number)
            .first()
        )
        if existing:
            print(f"Student already exists: {existing.student_number}")
            return

        student = Student(
            student_number=student_number,
            full_name=full_name,
            email=email,
            national_id=national_id,
            phone_number=phone_number,
            major=major,
            entry_year=entry_year,
            units_taken=0,
            mark=None,
            password_hash=get_password_hash(password),
            is_active=True,
        )

        db.add(student)
        db.commit()
        db.refresh(student)

        print(f"Seeded student: id={student.id}, student_number={student.student_number}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
