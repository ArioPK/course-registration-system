# backend/app/services/security.py

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError

# High-level Argon2id hasher with sane defaults (RFC 9106 / OWASP style)
pwd_hasher = PasswordHasher()

def get_password_hash(password: str) -> str:
    """
    Hash the provided plain-text password using Argon2id.

    The returned string includes all parameters and the salt,
    so it can be stored directly in the database.
    """
    return pwd_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify the provided plain-text password against a stored Argon2id hash.

    Returns True if the password is correct, False otherwise.
    """
    try:
        pwd_hasher.verify(hashed_password, plain_password)
        return True
    except (VerifyMismatchError, InvalidHashError):
        return False
