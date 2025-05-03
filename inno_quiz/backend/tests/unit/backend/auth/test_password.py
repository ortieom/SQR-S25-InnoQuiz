"""Test password utilities."""

from inno_quiz.backend.auth.password import get_password_hash, verify_password


def test_password_hashing():
    """Test that password hashing works correctly."""
    # Given
    password = "testpassword123"

    # When
    hashed_password = get_password_hash(password)

    # Then
    assert hashed_password != password
    assert verify_password(password, hashed_password)


def test_incorrect_password_verification():
    """Test that password verification fails for incorrect passwords."""
    # Given
    password = "testpassword123"
    wrong_password = "wrongpassword123"

    # When
    hashed_password = get_password_hash(password)

    # Then
    assert not verify_password(wrong_password, hashed_password)


def test_password_hash_uniqueness():
    """Test that same password produces different hashes."""
    # Given
    password = "testpassword123"

    # When
    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)

    # Then
    assert hash1 != hash2  # Each hash should be different due to salt
    assert verify_password(password, hash1)
    assert verify_password(password, hash2)
