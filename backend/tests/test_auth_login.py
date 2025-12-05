# backend/tests/test_auth_login.py

from sqlalchemy.orm import Session

from backend.app.models.admin import Admin
from backend.app.services.security import get_password_hash


def test_admin_login_success(client, db_session: Session) -> None:
    """
    End-to-end test:
    - Insert an Admin into the test database.
    - Call POST /auth/login with correct credentials.
    - Expect HTTP 200 and a valid access_token in the response.
    """
    # Arrange: insert a test admin in the test DB
    username = "testadmin"
    plain_password = "admin123"
    hashed_password = get_password_hash(plain_password)

    admin = Admin(
        username=username,
        password_hash=hashed_password,
        national_id="1234567890",
        email="testadmin@example.com",
        is_active=True,
    )
    db_session.add(admin)
    db_session.commit()

    # Act: call the login endpoint via the TestClient
    response = client.post(
        "/auth/login",
        json={"username": username, "password": plain_password},
    )

    # Assert: successful login with JWT token
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
