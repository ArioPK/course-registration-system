from backend.app.database import SessionLocal
from backend.app.models.professor import Professor


def main() -> None:
    db = SessionLocal()
    try:
        prof = (
            db.query(Professor)
            .filter(Professor.professor_code == "p123456")
            .first()
        )
        print(prof)
    finally:
        db.close()


if __name__ == "__main__":
    main()
