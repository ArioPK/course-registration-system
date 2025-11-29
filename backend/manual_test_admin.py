"""
Manual sanity test for the Admin ORM model.

Steps:
1. run: python backend/create_db.py
2.run: python backend/manual_test_admin.py
"""

from app.database import SessionLocal
from app.models.admin import Admin


def main() -> None:
    db = SessionLocal()
    try:
        # 1. Create a new Admin instance
        new_admin = Admin(
            username="test_admin",
            national_id="1234567890",
            email="test_admin@example.com",
            password_hash="dummy_hashed_password",
        )

        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)

        print("Inserted admin:", new_admin)

        # 2. Query it back
        fetched = db.query(Admin).filter_by(username="test_admin").first()
        print("Fetched admin:", fetched)

        if fetched is None:
            print("❌ Admin was not found in the database.")
        else:
            print("✅ Admin insert + query test passed.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
