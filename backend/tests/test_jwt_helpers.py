from datetime import timedelta

from backend.app.config.settings import settings
from backend.app.services.jwt import create_access_token, decode_access_token


def test_decode_access_token_includes_role_and_sub() -> None:
    token = create_access_token(
        data={"sub": "admin_test", "role": "admin"},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    decoded = decode_access_token(token)

    assert decoded["sub"] == "admin_test"
    assert decoded["role"] == "admin"
    assert "exp" in decoded
