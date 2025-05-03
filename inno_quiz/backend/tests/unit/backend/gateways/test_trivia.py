"""Test trivia gateway functionality."""
from unittest.mock import MagicMock, patch

import pytest
import requests

from backend.gateways.trivia import TriviaGateway, TriviaQuestion


@pytest.fixture
def mock_response_success():
    """Mock successful response from Trivia API."""
    mock = MagicMock()
    mock.status_code = 200
    mock.raise_for_status = MagicMock()
    mock.json = MagicMock(return_value={
        "response_code": 0,
        "results": [
            {
                "category": "Science: Computers",
                "type": "multiple",
                "difficulty": "medium",
                "question": "What does CPU stand for?",
                "correct_answer": "Central Processing Unit",
                "incorrect_answers": [
                    "Central Process Unit",
                    "Computer Personal Unit",
                    "Central Processor Unit"
                ]
            },
            {
                "category": "Science: Computers",
                "type": "multiple",
                "difficulty": "easy",
                "question": "What does the 'MP' stand for in MP3?",
                "correct_answer": "Moving Picture",
                "incorrect_answers": [
                    "Music Player",
                    "Multi Pass",
                    "Micro Point"
                ]
            }
        ]
    })
    return mock


@pytest.fixture
def mock_response_error():
    """Mock error response from Trivia API."""
    mock = MagicMock()
    mock.status_code = 200
    mock.raise_for_status = MagicMock()
    mock.json = MagicMock(return_value={"response_code": 1, "results": []})
    return mock


@pytest.fixture
def mock_response_http_error():
    """Mock HTTP error response from Trivia API."""
    mock = MagicMock()
    mock.raise_for_status = MagicMock(side_effect=requests.HTTPError(
        "404 Not Found",
        response=MagicMock(status_code=404)
    ))
    return mock


def test_get_questions_success(mock_response_success):
    """Test successfully getting trivia questions."""
    # Given
    trivia_gateway = TriviaGateway()

    # When
    with patch("requests.get", return_value=mock_response_success):
        questions = trivia_gateway.get_questions(amount=2)

    # Then
    assert len(questions) == 2
    assert isinstance(questions[0], TriviaQuestion)
    assert questions[0].category == "Science: Computers"
    assert questions[0].question == "What does CPU stand for?"
    assert questions[0].correct_answer == "Central Processing Unit"
    assert len(questions[0].incorrect_answers) == 3

    assert questions[1].difficulty == "easy"
    assert questions[1].correct_answer == "Moving Picture"


def test_get_questions_with_parameters(mock_response_success):
    """Test getting trivia questions with specific parameters."""
    # Given
    trivia_gateway = TriviaGateway()

    # When
    with patch("requests.get", return_value=mock_response_success) as mock_get:
        trivia_gateway.get_questions(
            amount=5,
            category=9,
            difficulty="medium",
            question_type="multiple"
        )

    # Then
    # Verify the correct parameters were passed
    mock_get.assert_called_once()
    call_args = mock_get.call_args
    assert "params" in call_args[1]
    params = call_args[1]["params"]
    assert params["amount"] == 5
    assert params["category"] == 9
    assert params["difficulty"] == "medium"
    assert params["type"] == "multiple"


def test_get_questions_api_error(mock_response_error):
    """Test handling API error response."""
    # Given
    trivia_gateway = TriviaGateway()

    # When/Then
    with patch("requests.get", return_value=mock_response_error):
        with pytest.raises(ValueError) as excinfo:
            trivia_gateway.get_questions()

    assert "Not enough questions available" in str(excinfo.value)


def test_get_questions_http_error(mock_response_http_error):
    """Test handling HTTP error response."""
    # Given
    trivia_gateway = TriviaGateway()

    # When/Then
    with patch("requests.get", return_value=mock_response_http_error):
        with pytest.raises(ValueError) as excinfo:
            trivia_gateway.get_questions()

    assert "HTTP error from Trivia API" in str(excinfo.value)


def test_get_questions_connection_error():
    """Test handling connection error."""
    # Given
    trivia_gateway = TriviaGateway()

    # When/Then
    with patch("requests.get", side_effect=requests.RequestException("Connection error")):
        with pytest.raises(ConnectionError) as excinfo:
            trivia_gateway.get_questions()

    assert "Error connecting to Trivia API" in str(excinfo.value)
