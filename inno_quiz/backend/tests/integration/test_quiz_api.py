"""Integration tests for quiz API endpoints."""

from uuid import UUID, uuid4
import pytest

from fastapi.testclient import TestClient

from inno_quiz.backend.models.question import Question
from inno_quiz.backend.models.quiz import Quiz
from inno_quiz.backend.models.answer_option import AnswerOption
from inno_quiz.backend.models.user import User
from inno_quiz.backend.main import app
from inno_quiz.backend.db import get_db
from inno_quiz.backend.gateways.trivia import TriviaQuestion


@pytest.fixture
def unauthenticated_client(db_session):
    """Create a client without authentication."""

    # Override the get_db dependency to use the test database
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app=app) as test_client:
        # Clear any cookies that might be set
        test_client.cookies.clear()
        yield test_client

    # Reset the overrides
    app.dependency_overrides = {}


@pytest.fixture
def authenticated_client(client: TestClient, db_session):
    """Create an authenticated client with a test user."""
    # Create a test user
    username = "testuser"
    password = "testpassword123"

    # Check if user already exists
    existing_user = db_session.query(User).filter(User.username == username).first()
    if not existing_user:
        user_data = {"username": username, "password": password}
        client.post("/v1/users/create", json=user_data)

    # Login to get token
    response = client.post(
        "/v1/users/login",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200, f"Failed to login: {response.json()}"
    token = response.json()["access_token"]

    # Create a client with the auth token in cookies
    client.cookies.set("access_token", f"Bearer {token}")
    return client


@pytest.fixture
def test_quiz(authenticated_client, db_session):
    """Create a test quiz for use in tests."""
    quiz_data = {
        "name": "API Test Quiz",
        "category": 9,  # general_knowledge
        "is_submitted": False,
    }

    response = authenticated_client.post("/v1/quiz/", json=quiz_data)
    assert response.status_code == 201

    quiz_id = response.json()["id"]
    return quiz_id


@pytest.fixture
def unauthenticated_test_quiz(db_session):
    """Create a quiz ID for unauthenticated tests without actually creating it in the database."""
    return str(uuid4())


def test_create_quiz(authenticated_client, db_session):
    """Test creating a new quiz."""
    # Given
    quiz_data = {
        "name": "Test Integration Quiz",
        "category": 9,  # general_knowledge
        "is_submitted": False,
    }

    # When
    response = authenticated_client.post("/v1/quiz/", json=quiz_data)

    # Then
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == quiz_data["name"]
    assert data["category"] == quiz_data["category"]
    assert data["is_submitted"] == quiz_data["is_submitted"]
    assert "id" in data
    assert "created_at" in data
    assert "author_username" in data
    assert data["author_username"] == "testuser"

    # Verify the quiz is in the database
    quiz_id = UUID(data["id"])
    db_quiz = db_session.query(Quiz).filter(Quiz.id == quiz_id).first()
    assert db_quiz is not None
    assert db_quiz.name == quiz_data["name"]
    assert int(db_quiz.category) == quiz_data["category"]
    assert db_quiz.is_submitted == quiz_data["is_submitted"]


def test_submit_quiz(authenticated_client, db_session):
    """Test submitting a quiz."""
    # Given - Create a quiz first
    quiz_data = {"name": "Quiz to Submit", "category": 9, "is_submitted": False}
    create_response = authenticated_client.post("/v1/quiz/", json=quiz_data)
    assert create_response.status_code == 201
    quiz_id_str = create_response.json()["id"]

    # When
    response = authenticated_client.put(f"/v1/quiz/{quiz_id_str}/submit")

    # Then
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == quiz_data["name"]
    assert data["category"] == quiz_data["category"]
    assert data["is_submitted"]  # Should be updated to True
    assert data["id"] == quiz_id_str

    # Verify the quiz is updated in the database
    quiz_id = UUID(quiz_id_str)
    db_quiz = db_session.query(Quiz).filter(Quiz.id == quiz_id).first()
    assert db_quiz is not None
    assert db_quiz.is_submitted


def test_submit_nonexistent_quiz(authenticated_client, db_session):
    """Test submitting a quiz that doesn't exist."""
    # Given
    nonexistent_quiz_id = str(uuid4())

    # When
    response = authenticated_client.put(f"/v1/quiz/{nonexistent_quiz_id}/submit")

    # Then
    assert response.status_code == 404
    assert "Quiz does not exist" in response.json()["detail"]


def test_add_question(authenticated_client, test_quiz, db_session):
    """Test adding a question to a quiz."""
    # Given
    question_data = {
        "text": "What is the capital of France?",
        "options": ["Paris", "London", "Berlin", "Madrid"],
        "correct_options": [0],  # Paris is correct
    }

    # When
    response = authenticated_client.post(
        f"/v1/quiz/{test_quiz}/questions", json=question_data
    )

    # Then
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == question_data["text"]
    assert data["options"] == question_data["options"]
    assert data["correct_options"] == question_data["correct_options"]
    assert "id" in data

    # Verify question is in database
    question_id = data["id"]
    db_question = db_session.query(Question).filter(Question.id == question_id).first()
    assert db_question is not None
    assert db_question.text == question_data["text"]

    # Verify options are in database
    options = (
        db_session.query(AnswerOption)
        .filter(AnswerOption.question_id == question_id)
        .all()
    )
    assert len(options) == 4
    option_texts = [opt.text for opt in options]
    assert all(opt in option_texts for opt in question_data["options"])

    # Verify correct option is marked
    correct_options = [opt for opt in options if opt.is_correct]
    assert len(correct_options) == 1
    assert correct_options[0].text == "Paris"


def test_load_external_questions(authenticated_client, test_quiz, db_session, mocker):
    """Test loading questions from external API."""
    # Create questions using the actual TriviaQuestion model
    mock_questions = [
        TriviaQuestion(
            question="What is the capital of France?",
            correct_answer="Paris",
            incorrect_answers=["London", "Berlin", "Madrid"],
            category="Geography",
            type="multiple",
            difficulty="easy",
        ),
        TriviaQuestion(
            question="Who wrote 'Romeo and Juliet'?",
            correct_answer="William Shakespeare",
            incorrect_answers=["Charles Dickens", "Jane Austen", "Leo Tolstoy"],
            category="Literature",
            type="multiple",
            difficulty="medium",
        ),
    ]

    # Better mock that ensures our mock gets used
    mocker.patch(
        "inno_quiz.backend.service.quiz.trivia_gateway.get_questions",
        return_value=mock_questions,
    )

    # When
    response = authenticated_client.get(
        f"/v1/quiz/{test_quiz}/load_questions?count=2&category=9"
    )

    # Then
    assert response.status_code == 200
    data = response.json()
    assert data["quiz_id"] == test_quiz
    assert len(data["questions"]) == 2

    # Check first question
    q1 = data["questions"][0]
    assert q1["text"] == "What is the capital of France?"
    assert "Paris" in q1["options"]
    assert len(q1["options"]) == 4

    # Verify questions are in database
    try:
        # Try converting to UUID first
        uuid_quiz_id = UUID(test_quiz)
        question_count = (
            db_session.query(Question).filter(Question.quiz_id == uuid_quiz_id).count()
        )
    except (ValueError, AttributeError):
        # Fall back to string if needed
        question_count = (
            db_session.query(Question).filter(Question.quiz_id == test_quiz).count()
        )

    assert question_count >= 2  # At least the 2 we just added


def test_get_quiz_info(authenticated_client, test_quiz, db_session):
    """Test getting quiz information."""
    # Given
    # Add a question to the quiz
    question_data = {
        "text": "Test question?",
        "options": ["A", "B", "C", "D"],
        "correct_options": [0],
    }
    authenticated_client.post(f"/v1/quiz/{test_quiz}/questions", json=question_data)

    # When
    response = authenticated_client.get(f"/v1/quiz/{test_quiz}")

    # Then
    assert response.status_code == 200
    data = response.json()
    assert data["quiz_id"] == test_quiz
    assert data["name"] == "API Test Quiz"
    assert data["category"] == "9"  # As string
    assert data["question_count"] >= 1


def test_get_quiz_questions(authenticated_client, test_quiz, db_session):
    """Test getting all questions for a quiz."""
    # Given
    # Add a question to the quiz if not already present
    question_data = {
        "text": "Another test question?",
        "options": ["W", "X", "Y", "Z"],
        "correct_options": [2],
    }
    authenticated_client.post(f"/v1/quiz/{test_quiz}/questions", json=question_data)

    # When
    response = authenticated_client.get(f"/v1/quiz/{test_quiz}/questions")

    # Then
    assert response.status_code == 200
    data = response.json()
    assert data["quiz_id"] == test_quiz
    assert len(data["questions"]) >= 1

    # Check that our question is included
    questions = data["questions"]
    found = False
    for q in questions:
        if q["text"] == question_data["text"]:
            assert "W" in q["options"]
            assert "Y" in q["options"]
            assert 2 in q["correct_options"]
            found = True
            break

    assert found, "Added question not found in response"


def test_submit_quiz_answers(authenticated_client, test_quiz, db_session):
    """Test submitting answers for a quiz."""
    # Given
    # Add a question to the quiz
    question_data = {
        "text": "What is 2+2?",
        "options": ["3", "4", "5", "6"],
        "correct_options": [1],  # 4 is correct
    }
    question_response = authenticated_client.post(
        f"/v1/quiz/{test_quiz}/questions", json=question_data
    )
    question_id = question_response.json()["id"]

    # When
    submission_data = {
        "quiz_id": test_quiz,
        "user_id": "will_be_overridden_by_endpoint",  # This will be set by the endpoint
        "answers": [
            {"question_id": question_id, "selected_options": [1]}  # Correct answer
        ],
        "completion_time": 10.5,
    }

    response = authenticated_client.post(
        f"/v1/quiz/{test_quiz}/answers", json=submission_data
    )

    # Then
    assert response.status_code == 200
    data = response.json()
    assert data["quiz_id"] == test_quiz
    assert data["score"] == 1
    assert data["total"] >= 1
    assert data["completion_time"] == 10.5
    assert "rank" in data


def test_get_leaderboard(authenticated_client, test_quiz, db_session):
    """Test getting the quiz leaderboard."""
    # Given
    # Ensure we have a submission to appear on the leaderboard
    test_submit_quiz_answers(authenticated_client, test_quiz, db_session)

    # When
    response = authenticated_client.get(f"/v1/quiz/{test_quiz}/leaderboard")

    # Then
    assert response.status_code == 200
    data = response.json()
    assert data["quiz_id"] == test_quiz
    assert data["quiz_name"] == "API Test Quiz"
    assert "entries" in data
    assert len(data["entries"]) >= 1

    # Check the entry format
    entry = data["entries"][0]
    assert "username" in entry
    assert "score" in entry
    assert "completion_time" in entry
    assert "date" in entry


def test_unauthorized_access(unauthenticated_client, unauthenticated_test_quiz):
    """Test that endpoints require authentication."""
    # Try to access a protected user endpoint
    response = unauthenticated_client.get("/v1/users/me")
    print(f"Response status code: {response.status_code}")
    print(f"Response body: {response.text}")
    print(f"Response headers: {response.headers}")

    # For debug purposes, check if cookies are being sent
    print(f"Client cookies: {unauthenticated_client.cookies}")

    assert response.status_code == 401, "User endpoint should require authentication"

    # Try a POST request that should be protected
    question_data = {
        "text": "What is the capital of France?",
        "options": ["Paris", "London", "Berlin", "Madrid"],
        "correct_options": [0],
    }

    response = unauthenticated_client.post(
        f"/v1/quiz/{unauthenticated_test_quiz}/questions", json=question_data
    )
    print(f"POST response status: {response.status_code}")
    assert response.status_code == 401, "POST endpoint should require authentication"

    # Try a submission that should be protected
    submission_data = {
        "quiz_id": unauthenticated_test_quiz,
        "user_id": "some_user_id",
        "answers": [],
        "completion_time": 10.5,
    }

    response = unauthenticated_client.post(
        f"/v1/quiz/{unauthenticated_test_quiz}/answers", json=submission_data
    )
    assert (
        response.status_code == 401
    ), "Submission endpoint should require authentication"
