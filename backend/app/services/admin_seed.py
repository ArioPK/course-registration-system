# backend/app/services/admin_seed.py

from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session  # type: ignore

from ..models.admin import Admin
from .security import get_password_hash


def create_initial_admin(
    db: Session,
    username: str,
    password: str,
    *,
    email: Optional[str] = None,
    national_id: Optional[str] = None,
) -> None:
    """
    Ensure there is an initial admin with the given username.

    - If an admin with this username already exists, do nothing.
    - If not, create one using the provided username and password.

    Args:
        db: SQLAlchemy SessionLocal instance.
        username: Initial admin username (e.g., "admin").
        password: Plain-text password to hash and store.
        email: Optional email for the admin. If not provided, a default will be used.
        national_id: Optional national ID. If not provided, a placeholder will be used.
    """

    # Check if an admin with this username already exists
    existing_admin = (
        db.query(Admin)
        .filter(Admin.username == username)
        .first()
    )

    if existing_admin:
        print(f"[seed_admin] Admin with username '{username}' already exists (id={existing_admin.id}). Skipping seeding.")
        return

    # Apply simple defaults for fields that are required by the Admin model
    if email is None:
        email = f"{username}@example.com"  # dev/demo default; override via env if needed

    if national_id is None:
        national_id = "0000000000"  # dev/demo placeholder; override via env if needed

    hashed_password = get_password_hash(password)

    new_admin = Admin(
        username=username,
        national_id=national_id,
        email=email,
        password_hash=hashed_password,
        is_active=True,
    )

    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)

    print(
        f"[seed_admin] Created initial admin: "
        f"username='{new_admin.username}', id={new_admin.id}"
    )
