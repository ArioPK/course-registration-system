# backend/manual_test_hashing.py

from app.services.security import get_password_hash, verify_password

def test_password_hashing():
    # Sample plain password
    password = "admin"

    # Get the hashed password
    hashed_password = get_password_hash(password)
    print(f"Hashed password: {hashed_password}")

    # Verify the password matches the hash
    assert verify_password("admin", hashed_password) == True  # Should pass
    assert verify_password("wrongpass", hashed_password) == False  # Should fail

    print("✅ Password hashing and verification test passed.")

if __name__ == "__main__":
    test_password_hashing()
