# backend/manual_test_login.py

import json

import httpx # type: ignore


def main() -> None:
    url = "http://127.0.0.1:8000/auth/login"
    payload = {
        "username": "admin",
        "password": "admin123",
    }

    response = httpx.post(url, json=payload)
    print("Status code:", response.status_code)
    print("Response JSON:", response.json())

    if response.status_code == 200:
        data = response.json()
        access_token = data.get("access_token")
        token_type = data.get("token_type")
        print("access_token present?", bool(access_token))
        print("token_type:", token_type)

        assert access_token is not None
        assert token_type == "bearer"

        print("✅ Login manual test passed.")
    else:
        print("❌ Login failed when it should have succeeded.")


if __name__ == "__main__":
    main()
