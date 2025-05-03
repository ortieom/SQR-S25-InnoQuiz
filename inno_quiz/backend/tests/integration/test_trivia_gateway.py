"""Integration tests for Trivia API gateway.

These tests interact with the real Trivia API and may fail if the service is down.
They are marked with the 'external' marker so they can be skipped if needed.
"""
import pytest

from inno_quiz.backend.gateways.trivia import trivia_gateway


@pytest.mark.external
def test_get_questions_from_real_api():
    """Test getting questions from the real Trivia API."""
    try:
        # When
        questions = trivia_gateway.get_questions(amount=3)

        # Then
        assert len(questions) == 3
        for question in questions:
            assert question.category is not None
            assert question.question is not None
            assert question.correct_answer is not None
            assert len(question.incorrect_answers) > 0
    except (ConnectionError, ValueError) as e:
        pytest.skip(f"Skipping test due to external API error: {str(e)}")


@pytest.mark.external
def test_get_questions_with_filters():
    """Test getting questions with specific filters from real Trivia API."""
    try:
        # When - Get computer science (category 18) questions that are easy
        questions = trivia_gateway.get_questions(
            amount=2,
            category=18,
            difficulty="easy"
        )

        # Then
        assert len(questions) == 2
        for question in questions:
            assert "Science: Computers" in question.category
            assert question.difficulty == "easy"
    except (ConnectionError, ValueError) as e:
        pytest.skip(f"Skipping test due to external API error: {str(e)}")


@pytest.mark.external
def test_get_questions_invalid_parameters():
    """Test error handling with invalid parameters."""
    try:
        # When/Then - Invalid category
        with pytest.raises((ValueError, ConnectionError)):
            trivia_gateway.get_questions(
                amount=5,
                category=999  # Non-existent category
            )
    except Exception as e:
        pytest.skip(f"Skipping test due to external API issues: {str(e)}")
