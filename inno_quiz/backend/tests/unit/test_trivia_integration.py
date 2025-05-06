"""Unit tests for the trivia gateway integration with quiz service."""

import pytest
from unittest.mock import MagicMock, patch

from inno_quiz.backend.service import quiz_service
from inno_quiz.backend.service.errors import QuizNotFoundError


@pytest.fixture
def mock_trivia_gateway():
    """Fixture for mocking the trivia gateway."""
    with patch("inno_quiz.backend.service.quiz_service.trivia_gateway") as mock_gw:
        yield mock_gw


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
    quiz.id = "test-quiz-id"
    quiz.name = "Test Quiz"
    quiz.category = 9
    return quiz


@pytest.fixture
def mock_trivia_questions():
    """Fixture for creating mock trivia questions."""

    class MockTriviaQuestion:
        def __init__(self, question, correct_answer, incorrect_answers):
            self.question = question
            self.correct_answer = correct_answer
            self.incorrect_answers = incorrect_answers

    return [
        MockTriviaQuestion(
            "What is the capital of France?", "Paris", ["London", "Berlin", "Madrid"]
        ),
        MockTriviaQuestion(
            "Who wrote 'Romeo and Juliet'?",
            "William Shakespeare",
            ["Charles Dickens", "Jane Austen", "Leo Tolstoy"],
        ),
    ]


def test_load_external_questions(
    mock_repo, mock_db, mock_quiz, mock_trivia_gateway, mock_trivia_questions
):
    """Test loading questions from external API."""
    # Given
    quiz_id = mock_quiz.id
    count = 2
    category = "9"

    mock_repo.quiz.get_by_id.return_value = mock_quiz
    mock_trivia_gateway.get_questions.return_value = mock_trivia_questions

    # Mock question creation
    question1 = MagicMock()
    question1.id = "q1"
    question1.text = "What is the capital of France?"

    question2 = MagicMock()
    question2.id = "q2"
    question2.text = "Who wrote 'Romeo and Juliet'?"

    # Define side effect to return different questions on consecutive calls
    questions = [question1, question2]
    options_list = [
        [
            MagicMock(text="Paris", is_correct=True),
            MagicMock(text="London", is_correct=False),
            MagicMock(text="Berlin", is_correct=False),
            MagicMock(text="Madrid", is_correct=False),
        ],
        [
            MagicMock(text="William Shakespeare", is_correct=True),
            MagicMock(text="Charles Dickens", is_correct=False),
            MagicMock(text="Jane Austen", is_correct=False),
            MagicMock(text="Leo Tolstoy", is_correct=False),
        ],
    ]

    def create_question_side_effect(*args, **kwargs):
        return questions[mock_repo.question.create_with_options.call_count - 1]

    def get_options_side_effect(*args, **kwargs):
        # Find which question ID was passed
        question_id = args[1]
        if question_id == "q1":
            return options_list[0]
        else:
            return options_list[1]

    mock_repo.question.create_with_options.side_effect = create_question_side_effect
    mock_repo.answer_option.get_by_question_id.side_effect = get_options_side_effect

    # When
    with patch("uuid.UUID", side_effect=lambda x: x):
        result = quiz_service.load_external_questions(quiz_id, count, category, mock_db)

    # Then
    mock_repo.quiz.get_by_id.assert_called_once_with(mock_db, quiz_id)
    mock_trivia_gateway.get_questions.assert_called_once_with(
        amount=count, category=9  # Integer value after conversion
    )

    # Verify question creation calls
    assert mock_repo.question.create_with_options.call_count == 2

    # First question
    first_call_args = mock_repo.question.create_with_options.call_args_list[0][1]
    assert first_call_args["quiz_id"] == quiz_id
    assert first_call_args["text"] == "What is the capital of France?"
    assert "Paris" in first_call_args["options"]
    assert first_call_args["correct_options"] == [0]

    # Verify response
    assert result.quiz_id == quiz_id
    assert result.name == mock_quiz.name
    assert result.category == "9"
    assert len(result.questions) == 2

    # Check first question in response
    q1 = result.questions[0]
    assert q1.id == "q1"
    assert q1.text == "What is the capital of France?"
    assert "Paris" in q1.options
    assert q1.correct_options == [0]

    # Check second question in response
    q2 = result.questions[1]
    assert q2.id == "q2"
    assert q2.text == "Who wrote 'Romeo and Juliet'?"
    assert "William Shakespeare" in q2.options
    assert q2.correct_options == [0]


def test_load_external_questions_quiz_not_found(mock_repo, mock_db):
    """Test loading questions for a non-existent quiz."""
    # Given
    quiz_id = "nonexistent-quiz"
    count = 2
    category = "9"

    mock_repo.quiz.get_by_id.return_value = None

    # When / Then
    with patch("uuid.UUID", side_effect=lambda x: x):
        with pytest.raises(QuizNotFoundError):
            quiz_service.load_external_questions(quiz_id, count, category, mock_db)

    mock_repo.quiz.get_by_id.assert_called_once_with(mock_db, quiz_id)


def test_load_external_questions_non_numeric_category(
    mock_repo, mock_db, mock_quiz, mock_trivia_gateway, mock_trivia_questions
):
    """Test loading questions with a non-numeric category."""
    # Given
    quiz_id = mock_quiz.id
    count = 2
    category = "general_knowledge"  # Non-numeric

    mock_repo.quiz.get_by_id.return_value = mock_quiz
    mock_trivia_gateway.get_questions.return_value = mock_trivia_questions

    # Mock question creation (simplified)
    mock_question = MagicMock()
    mock_question.id = "test-id"
    mock_question.text = "Test Question"
    mock_repo.question.create_with_options.return_value = mock_question

    mock_options = [MagicMock(text="Option", is_correct=True)]
    mock_repo.answer_option.get_by_question_id.return_value = mock_options

    # When
    with patch("uuid.UUID", side_effect=lambda x: x):
        quiz_service.load_external_questions(quiz_id, count, category, mock_db)

    # Then
    mock_trivia_gateway.get_questions.assert_called_once_with(
        amount=count, category=None  # Should be None for non-numeric category
    )
