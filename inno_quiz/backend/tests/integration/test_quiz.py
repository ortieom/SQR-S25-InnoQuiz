"""Integration tests for quiz endpoints."""

import uuid
from fastapi.testclient import TestClient

from inno_quiz.backend.models.quiz import Quiz


def test_create_quiz(client: TestClient, db_session):
    """Test creating a new quiz."""
    # Given
    quiz_data = {
        "name": "Test Integration Quiz",
        "category": 9,  # general_knowledge
        "is_submitted": False,
    }

    # When
    response = client.post("/v1/quiz/", json=quiz_data)

    # Then
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == quiz_data["name"]
    assert data["category"] == quiz_data["category"]
    assert data["is_submitted"] == quiz_data["is_submitted"]
    assert "id" in data
    assert "created_at" in data
    assert "author_username" in data
    assert data["author_username"] == "tester"  # Hardcoded in endpoint

    # Verify the quiz is in the database
    quiz_id = uuid.UUID(data["id"])
    db_quiz = db_session.query(Quiz).filter(Quiz.id == quiz_id).first()
    assert db_quiz is not None
    assert db_quiz.name == quiz_data["name"]
    assert int(db_quiz.category) == quiz_data["category"]
    assert db_quiz.is_submitted == quiz_data["is_submitted"]


def test_submit_quiz(client: TestClient, db_session):
    """Test submitting a quiz."""
    # Given - Create a quiz first
    quiz_data = {"name": "Quiz to Submit", "category": 9, "is_submitted": False}
    create_response = client.post("/v1/quiz/", json=quiz_data)
    assert create_response.status_code == 201
    quiz_id_str = create_response.json()["id"]

    # When
    response = client.put(f"/v1/quiz/{quiz_id_str}/submit")

    # Then
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == quiz_data["name"]
    assert data["category"] == quiz_data["category"]
    assert data["is_submitted"] == True  # Should be updated to True
    assert data["id"] == quiz_id_str

    # Verify the quiz is updated in the database
    quiz_id = uuid.UUID(quiz_id_str)
    db_quiz = db_session.query(Quiz).filter(Quiz.id == quiz_id).first()
    assert db_quiz is not None
    assert db_quiz.is_submitted == True


def test_submit_nonexistent_quiz(client: TestClient, db_session):
    """Test submitting a quiz that doesn't exist."""
    # Given
    nonexistent_quiz_id = str(uuid.uuid4())

    # When
    response = client.put(f"/v1/quiz/{nonexistent_quiz_id}/submit")

    # Then
    assert response.status_code == 404
    assert "Quiz does not exist" in response.json()["detail"]
