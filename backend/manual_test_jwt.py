# backend/manual_test_jwt.py

from datetime import timedelta

from app.services.jwt import (
    create_access_token,
    decode_access_token,
    InvalidTokenError,
)


def test_jwt_helpers() -> None:
    # 1) Create a token for a sample admin
    payload = {"sub": "admin_username"}
    token = create_access_token(payload, expires_delta=timedelta(minutes=5))

    print(f"Access token: {token}")

    # 2) Decode the token and verify payload
    decoded = decode_access_token(token)
    print(f"Decoded payload: {decoded}")

    assert decoded["sub"] == "admin_username"
    print("✅ Valid token decode test passed.")

    # 3) Try to decode an obviously invalid token
    invalid_token = token + "corrupted"

    try:
        decode_access_token(invalid_token)
        print("❌ Invalid token was incorrectly accepted.")
    except InvalidTokenError:
        print("✅ Invalid token correctly rejected.")


if __name__ == "__main__":
    test_jwt_helpers()
