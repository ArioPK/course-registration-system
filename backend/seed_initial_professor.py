# backend/seed_initial_professor.py

import os

from backend.app.database import SessionLocal
from backend.app.models.professor import Professor
from backend.app.services.security import get_password_hash


def main() -> None:
    professor_code = os.getenv("INITIAL_PROFESSOR_CODE", "p123456")
    password = os.getenv("INITIAL_PROFESSOR_PASSWORD", "professor123")
    full_name = os.getenv("INITIAL_PROFESSOR_FULL_NAME", "Test Professor")
    email = os.getenv("INITIAL_PROFESSOR_EMAIL", "professor@example.com")

    db = SessionLocal()
    try:
        existing = (
            db.query(Professor)
            .filter(Professor.professor_code == professor_code)
            .first()
        )
        if existing:
            print("Initial professor already exists, skipping.")
            return

        prof = Professor(
            professor_code=professor_code,
            full_name=full_name,
            email=email,
            password_hash=get_password_hash(password),
            is_active=True,
        )

        db.add(prof)
        db.commit()
        db.refresh(prof)

        print(f"Seeded initial professor: id={prof.id}, code={prof.professor_code}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
