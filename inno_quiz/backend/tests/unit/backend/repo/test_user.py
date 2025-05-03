"""Test user repository functions."""

from inno_quiz.backend.models.user import User
from inno_quiz.backend.repo.user import (
    create_user,
    get_user_by_username,
    verify_username_unique,
)


def test_create_user(db_session):
    """Test creating a new user."""
    # Given
    username = "testuser_create"
    hashed_password = "hashedpassword123"

    # When
    user = create_user(db_session, username, hashed_password)

    # Then
    assert user.username == username
    assert user.password == hashed_password

    # Verify the user exists in the database
    db_user = db_session.query(User).filter(User.username == username).first()
    assert db_user is not None
    assert db_user.username == username
    assert db_user.password == hashed_password


def test_get_user_by_username_existing(db_session):
    """Test getting an existing user by username."""
    # Given
    username = "testuser_get"
    hashed_password = "hashedpassword123"
    user = User(username=username, password=hashed_password)
    db_session.add(user)
    db_session.commit()

    # When
    result = get_user_by_username(db_session, username)

    # Then
    assert result is not None
    assert result.username == username
    assert result.password == hashed_password


def test_get_user_by_username_nonexistent(db_session):
    """Test getting a non-existent user by username."""
    # Given
    username = "nonexistentuser"

    # When
    result = get_user_by_username(db_session, username)

    # Then
    assert result is None


def test_verify_username_unique_true(db_session):
    """Test verifying a username is unique when it doesn't exist."""
    # Given
    username = "newuser"

    # When
    result = verify_username_unique(db_session, username)

    # Then
    assert result is True


def test_verify_username_unique_false(db_session):
    """Test verifying a username is unique when it already exists."""
    # Given
    username = "existinguser"
    user = User(username=username, password="hashedpassword123")
    db_session.add(user)
    db_session.commit()

    # When
    result = verify_username_unique(db_session, username)

    # Then
    assert result is False
