# backend/seed_initial_admin.py

"""
One-off script to seed an initial admin user into the database.

Usage (from project root):
    python backend/seed_initial_admin.py

Environment variables :
    INITIAL_ADMIN_USERNAME
    INITIAL_ADMIN_PASSWORD
    INITIAL_ADMIN_EMAIL         (opt)
    INITIAL_ADMIN_NATIONAL_ID   (opt)

For local development, if these are not set, the script will fall back to
defaults like "admin" / "admin123". DO NOT use these defaults in a real
production environment.
"""

import os

from app.database import SessionLocal
from app.services.admin_seed import create_initial_admin


def main() -> None:
    # Read env-based username/password for the initial admin
    username = os.getenv("INITIAL_ADMIN_USERNAME", "admin")
    password = os.getenv("INITIAL_ADMIN_PASSWORD", "admin123")

    # Optional overrides for email and national ID
    email = os.getenv("INITIAL_ADMIN_EMAIL", f"{username}@example.com")
    national_id = os.getenv("INITIAL_ADMIN_NATIONAL_ID", "0000000000")

    if "INITIAL_ADMIN_PASSWORD" not in os.environ:
        print(
            "[seed_admin] WARNING: INITIAL_ADMIN_PASSWORD not set; using default 'admin123'. "
            "Do not use this default in a real production environment."
        )

    db = SessionLocal()
    try:
        create_initial_admin(
            db,
            username=username,
            password=password,
            email=email,
            national_id=national_id,
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()
