"""Unit tests for quiz service."""

import pytest
from unittest.mock import MagicMock, patch
from uuid import UUID

from backend.domain.quiz import QuizBase, QuizCreate, QuizRead
from backend.service import quiz as quiz_service
from backend.service.errors import QuizNotFoundError
from backend.models.quiz import Quiz


@pytest.fixture
def mock_quiz_repo():
    with patch("backend.repo.quiz") as mock_repo:
        yield mock_repo


def test_create_quiz_template(mock_quiz_repo):
    """Test create_quiz_template function."""
    # Given
    quiz_data = QuizBase(
        name="Test Quiz", category=9, is_submitted=False  # general_knowledge
    )
    author_username = "testuser"
    db_session = MagicMock()

    # Mock the repo's create method
    quiz_id = UUID("12345678-1234-5678-1234-567812345678")
    mock_quiz = Quiz(
        id=quiz_id,
        name=quiz_data.name,
        category=quiz_data.category,
        author_username=author_username,
        is_submitted=quiz_data.is_submitted,
    )
    mock_quiz_repo.create.return_value = mock_quiz

    # When
    result = quiz_service.create_quiz_template(
        quiz_data, author_username, db=db_session
    )

    # Then
    mock_quiz_repo.create.assert_called_once()
    assert isinstance(mock_quiz_repo.create.call_args[1]["obj_in"], QuizCreate)
    assert mock_quiz_repo.create.call_args[1]["obj_in"].name == quiz_data.name
    assert mock_quiz_repo.create.call_args[1]["obj_in"].category == quiz_data.category
    assert (
        mock_quiz_repo.create.call_args[1]["obj_in"].author_username == author_username
    )
    assert mock_quiz_repo.create.call_args[1]["obj_in"].is_submitted == False
    assert result == mock_quiz


def test_submit_quiz_success(mock_quiz_repo):
    """Test submit_quiz function for a successful submission."""
    # Given
    quiz_id = UUID("12345678-1234-5678-1234-567812345678")
    db_session = MagicMock()

    # Mock the repo methods
    mock_quiz = Quiz(
        id=quiz_id,
        name="Test Quiz",
        category=9,
        author_username="testuser",
        is_submitted=False,
    )
    mock_quiz_repo.get_by_id.return_value = mock_quiz

    mock_updated_quiz = Quiz(
        id=quiz_id,
        name="Test Quiz",
        category=9,
        author_username="testuser",
        is_submitted=True,
    )
    mock_quiz_repo.update.return_value = mock_updated_quiz

    # When
    result = quiz_service.submit_quiz(quiz_id, db=db_session)

    # Then
    mock_quiz_repo.get_by_id.assert_called_once_with(db_session, quiz_id)
    mock_quiz_repo.update.assert_called_once()
    assert mock_quiz_repo.update.call_args[1]["obj_in"] == {"is_submitted": True}
    assert result == mock_updated_quiz


def test_submit_quiz_not_found(mock_quiz_repo):
    """Test submit_quiz function when quiz is not found."""
    # Given
    quiz_id = UUID("12345678-1234-5678-1234-567812345678")
    db_session = MagicMock()

    # Mock the repo methods to return None for get_by_id
    mock_quiz_repo.get_by_id.return_value = None

    # When & Then
    with pytest.raises(QuizNotFoundError):
        quiz_service.submit_quiz(quiz_id, db=db_session)

    mock_quiz_repo.get_by_id.assert_called_once_with(db_session, quiz_id)
    mock_quiz_repo.update.assert_not_called()
