"""Test JWT token utilities."""
import time
from datetime import timedelta
from unittest.mock import patch, MagicMock

import pytest
from fastapi import HTTPException
from jose import jwt

from inno_quiz.backend.auth.jwt import create_access_token, get_current_user
from inno_quiz.backend.config import settings


def test_create_access_token():
    """Test creation of JWT access token."""
    # Given
    data = {"sub": "testuser"}

    # When
    token = create_access_token(data)

    # Then
    payload = jwt.decode(
        token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )
    assert payload["sub"] == "testuser"
    # Check expiration is in the future
    assert payload["exp"] > time.time()


def test_create_access_token_with_expiry():
    """Test creation of JWT access token with custom expiry."""
    # Given
    data = {"sub": "testuser"}
    expires_delta = timedelta(minutes=30)

    # When
    token = create_access_token(data, expires_delta)

    # Then
    payload = jwt.decode(
        token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )
    assert payload["sub"] == "testuser"
    # Approximately 30 minutes from now (with small buffer for test execution time)
    # 29.9 minutes in seconds = 1794
    now = time.time()
    assert payload["exp"] > now + 1794
    assert payload["exp"] < now + 1860  # 31 minutes


def test_get_current_user_valid_token():
    """Test getting current user with valid token."""
    # Given
    username = "testuser"
    mock_user = MagicMock()
    mock_user.username = username

    mock_db = MagicMock()
    mock_get_user = MagicMock(return_value=mock_user)

    # Create a valid token
    token = create_access_token({"sub": username})

    # When/Then
    with patch("inno_quiz.backend.auth.jwt.get_user_by_username", mock_get_user):
        user = get_current_user(token, mock_db)
        assert user == mock_user
        mock_get_user.assert_called_once_with(mock_db, username=username)


def test_get_current_user_invalid_token():
    """Test getting current user with invalid token."""
    # Given
    mock_db = MagicMock()
    invalid_token = "invalid.token.value"

    # When/Then
    with pytest.raises(HTTPException) as excinfo:
        get_current_user(invalid_token, mock_db)

    assert excinfo.value.status_code == 401
    assert "Could not validate credentials" in excinfo.value.detail


def test_get_current_user_missing_username():
    """Test getting current user with token missing username."""
    # Given
    mock_db = MagicMock()
    # Create token with no sub claim
    token = create_access_token({"key": "value"})

    # When/Then
    with pytest.raises(HTTPException) as excinfo:
        get_current_user(token, mock_db)

    assert excinfo.value.status_code == 401
    assert "Could not validate credentials" in excinfo.value.detail


def test_get_current_user_nonexistent_user():
    """Test getting current user when user doesn't exist in database."""
    # Given
    username = "nonexistentuser"
    mock_db = MagicMock()
    mock_get_user = MagicMock(return_value=None)  # User not found

    # Create a valid token
    token = create_access_token({"sub": username})

    # When/Then
    with patch("inno_quiz.backend.auth.jwt.get_user_by_username", mock_get_user):
        with pytest.raises(HTTPException) as excinfo:
            get_current_user(token, mock_db)

        assert excinfo.value.status_code == 401
        assert "Could not validate credentials" in excinfo.value.detail
        mock_get_user.assert_called_once_with(mock_db, username=username)
