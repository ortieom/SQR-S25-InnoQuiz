from uuid import UUID

from pydantic import BaseModel


class QuestionBase(BaseModel):
    """Base model for question data with the question text."""
    text: str


class QuestionCreate(QuestionBase):
    """Model for creating a new question, extends QuestionBase with quiz association."""
    quiz_id: UUID


class QuestionRead(QuestionBase):
    """
    Model representing a question with all fields including system-generated ID.
    Used for API responses.
    """
    id: int
    quiz_id: UUID
