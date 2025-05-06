"""Integration tests for user authentication endpoints."""

import uuid
from fastapi.testclient import TestClient

from inno_quiz.backend.models.user import User


def test_register_user(client: TestClient, db_session):
    """Test user registration endpoint."""
    # Given
    # Generate a unique username to avoid conflicts
    unique_username = f"testuser_{uuid.uuid4().hex[:8]}"
    user_data = {"username": unique_username, "password": "testpassword123"}

    # When
    response = client.post("/v1/users/create", json=user_data)

    # Then
    assert response.status_code == 201
    assert response.json()["username"] == user_data["username"]

    # Verify user is in database with hashed password
    db_user = (
        db_session.query(User).filter(User.username == user_data["username"]).first()
    )
    assert db_user is not None
    assert db_user.username == user_data["username"]
    assert db_user.password != user_data["password"]  # Password should be hashed


def test_register_duplicate_user(client: TestClient, db_session):
    """Test registering a user with a duplicate username."""
    # Given
    username = "duplicateuser"
    # Create a user first
    user_data = {"username": username, "password": "testpassword123"}
    client.post("/v1/users/create", json=user_data)

    # When - try to create the same user again
    response = client.post("/v1/users/create", json=user_data)

    # Then
    assert response.status_code == 400
    assert "Username already registered" in response.json()["detail"]


def test_login_success(client: TestClient, db_session):
    """Test successful login."""
    # Given
    user_data = {"username": "loginuser", "password": "testpassword123"}
    # Create a user first
    client.post("/v1/users/create", json=user_data)

    # When
    response = client.post(
        "/v1/users/login",
        data={"username": user_data["username"], "password": user_data["password"]},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    # Then
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    # Check cookie was set
    cookies = response.cookies
    assert "access_token" in cookies
    cookie_value = cookies["access_token"]
    # Remove any quotes if present
    if cookie_value.startswith('"') and cookie_value.endswith('"'):
        cookie_value = cookie_value[1:-1]
    assert cookie_value.startswith("Bearer ")


def test_login_invalid_credentials(client: TestClient, db_session):
    """Test login with invalid credentials."""
    # Given
    user_data = {"username": "invaliduser", "password": "testpassword123"}
    # Create a user first
    client.post("/v1/users/create", json=user_data)

    # When - try to login with wrong password
    response = client.post(
        "/v1/users/login",
        data={"username": user_data["username"], "password": "wrongpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    # Then
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]
