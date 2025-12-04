# backend/manual_test_initial_admin.py

from app.database import SessionLocal
from app.models.admin import Admin
from app.services.security import verify_password


def main() -> None:
    db = SessionLocal()
    try:
        admin = db.query(Admin).filter(Admin.username == "admin").first()

        if admin is None:
            print("❌ No admin with username 'admin' found.")
            return

        print(f"✅ Found admin: {admin}")

        # Verify the known password (assuming default 'admin123' for dev)
        is_valid = verify_password("admin123", admin.password_hash)
        print(f"Password 'admin123' valid? {is_valid}")

        if is_valid:
            print("✅ Password verification passed.")
        else:
            print("❌ Password verification failed.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
