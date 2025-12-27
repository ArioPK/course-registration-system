import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.dependencies.auth import get_current_admin


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def get_admin_token(client):
    response = client.post('/auth/login', json={"username": "admin", "password": "admin123"})
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def get_student_token(client):
    response = client.post('/auth/student/login', json={"student_number": "std1", "password": "1234"})
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def get_professor_token(client: TestClient, db_session):
    # Function to get professor token
    pass


def test_settings_units_get_missing_token_returns_401(client):
    response = client.get("/api/courses")
    assert response.status_code == 401, response.text


def test_settings_units_put_missing_token_returns_401(client):
    response = client.put("/api/courses/1")
    assert response.status_code == 401, response.text


def test_settings_units_wrong_role_token_returns_403(client, get_student_token):
    token = get_student_token
    response = client.get(
        "/api/courses", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403, response.text


def test_settings_units_get_returns_expected_shape(client, get_admin_token):
    token = get_admin_token
    response = client.get("/api/courses", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert "min_units" in data[0]
    assert "max_units" in data[0]


def test_settings_units_put_accepts_snake_case(client, get_admin_token):
    token = get_admin_token
    response = client.put(
        "/api/courses/1",
        json={"min_units": 10, "max_units": 20},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text


def test_settings_units_put_accepts_camel_case(client, get_admin_token):
    token = get_admin_token
    response = client.put(
        "/api/courses/1",
        json={"minUnits": 10, "maxUnits": 20},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text


def test_settings_units_put_invalid_range_returns_400(client, get_admin_token):
    token = get_admin_token
    response = client.put(
        "/api/courses/1",
        json={"minUnits": 30, "maxUnits": 10},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400, response.text


def test_settings_units_put_missing_field_returns_400(client, get_admin_token):
    token = get_admin_token
    response = client.put(
        "/api/courses/1",
        json={"minUnits": 10},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400, response.text
