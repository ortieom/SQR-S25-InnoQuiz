"""Unit tests for quiz service functions."""

import uuid
import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

from inno_quiz.backend.service import quiz_service
from inno_quiz.backend.service.errors import QuizNotFoundError, UserNotFoundError
from inno_quiz.backend.domain.question_request import QuestionRequest
from inno_quiz.backend.domain.quiz_request import (
    QuizSubmissionRequest,
    QuizAnswerRequest,
)


@pytest.fixture
def mock_repo():
    """Fixture for mocking repository objects."""
    with patch("inno_quiz.backend.service.quiz_service.repo") as mock_repo:
        yield mock_repo


@pytest.fixture
def mock_db():
    """Fixture for mocking database session."""
    return MagicMock()


@pytest.fixture
def mock_quiz():
    """Fixture for creating a mock quiz."""
    quiz = MagicMock()
    quiz.id = str(uuid.uuid4())
    quiz.name = "Test Quiz"
    quiz.category = 9
    quiz.author_username = "testuser"
    quiz.created_at = datetime.now()
    return quiz


@pytest.fixture
def mock_question_with_options():
    """Fixture for creating a mock question with options."""
    question = MagicMock()
    question.id = str(uuid.uuid4())
    question.text = "Test Question"

    option1 = MagicMock()
    option1.text = "Option A"
    option1.is_correct = True

    option2 = MagicMock()
    option2.text = "Option B"
    option2.is_correct = False

    mock_options = [option1, option2]

    return question, mock_options


def test_add_question(mock_repo, mock_db, mock_quiz, mock_question_with_options):
    """Test adding a question to a quiz."""
    # Given
    quiz_id = mock_quiz.id
    question_request = QuestionRequest(
        text="Test Question", options=["Option A", "Option B"], correct_options=[0]
    )

    mock_repo.quiz.get_by_id.return_value = mock_quiz

    question, options = mock_question_with_options
    mock_repo.question.create_with_options.return_value = question
    mock_repo.answer_option.get_by_question_id.return_value = options

    # When
    with patch("uuid.UUID", side_effect=lambda x: x):
        result = quiz_service.add_question(quiz_id, question_request, mock_db)

    # Then
    mock_repo.quiz.get_by_id.assert_called_once_with(mock_db, quiz_id)
    mock_repo.question.create_with_options.assert_called_once_with(
        db=mock_db,
        quiz_id=quiz_id,
        text=question_request.text,
        options=question_request.options,
        correct_options=question_request.correct_options,
    )
    mock_repo.answer_option.get_by_question_id.assert_called_once_with(
        mock_db, question.id
    )

    assert result.id == str(question.id)
    assert result.text == question.text
    assert result.options == [opt.text for opt in options]
    assert result.correct_options == [0]  # Index 0 is correct


def test_add_question_quiz_not_found(mock_repo, mock_db):
    """Test adding a question to a non-existent quiz."""
    # Given
    quiz_id = str(uuid.uuid4())
    question_request = QuestionRequest(
        text="Test Question", options=["Option A", "Option B"], correct_options=[0]
    )

    mock_repo.quiz.get_by_id.return_value = None

    # When / Then
    with patch("uuid.UUID", side_effect=lambda x: x):
        with pytest.raises(QuizNotFoundError):
            quiz_service.add_question(quiz_id, question_request, mock_db)


def test_get_quiz_info(mock_repo, mock_db, mock_quiz):
    """Test getting quiz information."""
    # Given
    quiz_id = mock_quiz.id
    mock_repo.quiz.get_by_id.return_value = mock_quiz
    mock_repo.question.count_by_quiz_id.return_value = 5

    # When
    with patch("uuid.UUID", side_effect=lambda x: x):
        result = quiz_service.get_quiz_info(quiz_id, mock_db)

    # Then
    mock_repo.quiz.get_by_id.assert_called_once_with(mock_db, quiz_id)
    mock_repo.question.count_by_quiz_id.assert_called_once_with(mock_db, quiz_id)

    assert result.quiz_id == str(mock_quiz.id)
    assert result.name == mock_quiz.name
    assert result.category == str(mock_quiz.category)
    assert result.author == mock_quiz.author_username
    assert result.creation_date == mock_quiz.created_at
    assert result.question_count == 5


def test_get_quiz_info_not_found(mock_repo, mock_db):
    """Test getting info for a non-existent quiz."""
    # Given
    quiz_id = str(uuid.uuid4())
    mock_repo.quiz.get_by_id.return_value = None

    # When / Then
    with patch("uuid.UUID", side_effect=lambda x: x):
        with pytest.raises(QuizNotFoundError):
            quiz_service.get_quiz_info(quiz_id, mock_db)


def test_get_quiz_questions(mock_repo, mock_db, mock_quiz, mock_question_with_options):
    """Test getting all questions for a quiz."""
    # Given
    quiz_id = mock_quiz.id
    question, options = mock_question_with_options

    mock_repo.quiz.get_by_id.return_value = mock_quiz
    mock_repo.question.get_by_quiz_id.return_value = [question]
    mock_repo.answer_option.get_by_question_id.return_value = options

    # When
    with patch("uuid.UUID", side_effect=lambda x: x):
        result = quiz_service.get_quiz_questions(quiz_id, mock_db)

    # Then
    mock_repo.quiz.get_by_id.assert_called_once_with(mock_db, quiz_id)
    mock_repo.question.get_by_quiz_id.assert_called_once_with(mock_db, quiz_id)
    mock_repo.answer_option.get_by_question_id.assert_called_once_with(
        mock_db, question.id
    )

    assert result.quiz_id == str(mock_quiz.id)
    assert result.name == mock_quiz.name
    assert result.category == str(mock_quiz.category)
    assert len(result.questions) == 1

    question_response = result.questions[0]
    assert question_response.id == str(question.id)
    assert question_response.text == question.text
    assert question_response.options == [opt.text for opt in options]
    assert question_response.correct_options == [0]  # Index 0 is correct


def test_submit_quiz_answers(mock_repo, mock_db, mock_quiz, mock_question_with_options):
    """Test submitting answers for a quiz."""
    # Given
    quiz_id = mock_quiz.id
    username = "test_user"  # Use username instead of UUID
    question, options = mock_question_with_options
    question_id = question.id

    # Mock user
    mock_user = MagicMock()
    mock_user.username = username

    # Mock attempt
    mock_attempt = MagicMock()
    mock_attempt.id = str(uuid.uuid4())

    # Set up repository mocks
    mock_repo.quiz.get_by_id.return_value = mock_quiz
    mock_repo.user.get_by_username.return_value = mock_user
    mock_repo.question.count_by_quiz_id.return_value = 1
    mock_repo.question.get_by_id.return_value = question
    mock_repo.answer_option.get_by_question_id.return_value = options
    mock_repo.user_attempt.create.return_value = mock_attempt
    mock_repo.user_attempt.get_by_quiz_id.return_value = [mock_attempt]

    # Create the request
    request = QuizSubmissionRequest(
        quiz_id=quiz_id,
        user_id=username,  # Username instead of UUID
        answers=[
            QuizAnswerRequest(
                question_id=question_id, selected_options=[0]  # Correct answer
            )
        ],
        completion_time=10.5,
    )

    # When
    with patch("uuid.UUID", side_effect=lambda x: x):
        result = quiz_service.submit_quiz_answers(request, mock_db)

    # Then
    mock_repo.quiz.get_by_id.assert_called_once_with(mock_db, quiz_id)
    mock_repo.user.get_by_username.assert_called_once_with(mock_db, username)
    mock_repo.question.count_by_quiz_id.assert_called_once_with(mock_db, quiz_id)
    mock_repo.question.get_by_id.assert_called_once_with(mock_db, question_id)
    mock_repo.answer_option.get_by_question_id.assert_called_once_with(
        mock_db, question_id
    )

    mock_repo.user_attempt.create.assert_called_once_with(
        db=mock_db,
        username=username,  # Username instead of UUID
        quiz_id=quiz_id,  # Using the UUID object now
        score=1,  # Correct answer
        completion_time=10.5,
    )

    mock_repo.user_answer.create.assert_called_once_with(
        db=mock_db,
        attempt_id=mock_attempt.id,
        question_id=question_id,  # Using the UUID object now
        selected_options=[0],
    )

    assert result.quiz_id == str(mock_quiz.id)
    assert result.score == 1
    assert result.total == 1
    assert result.completion_time == 10.5
    assert result.rank == 1  # First attempt


def test_submit_quiz_answers_quiz_not_found(mock_repo, mock_db):
    """Test submitting answers for a non-existent quiz."""
    # Given
    quiz_id = str(uuid.uuid4())
    username = "test_user"  # Use username instead of UUID

    mock_repo.quiz.get_by_id.return_value = None

    request = QuizSubmissionRequest(
        quiz_id=quiz_id, user_id=username, answers=[], completion_time=10.5
    )

    # When / Then
    with patch("uuid.UUID", side_effect=lambda x: x):
        with pytest.raises(QuizNotFoundError):
            quiz_service.submit_quiz_answers(request, mock_db)


def test_submit_quiz_answers_user_not_found(mock_repo, mock_db, mock_quiz):
    """Test submitting answers with a non-existent user."""
    # Given
    quiz_id = mock_quiz.id
    username = "nonexistent_user"  # Use username instead of UUID

    mock_repo.quiz.get_by_id.return_value = mock_quiz
    mock_repo.user.get_by_username.return_value = None

    request = QuizSubmissionRequest(
        quiz_id=quiz_id, user_id=username, answers=[], completion_time=10.5
    )

    # When / Then
    with patch("uuid.UUID", side_effect=lambda x: x):
        with pytest.raises(UserNotFoundError):
            quiz_service.submit_quiz_answers(request, mock_db)
