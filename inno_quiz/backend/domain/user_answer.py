from datetime import datetime

from pydantic import BaseModel


class UserAnswerBase(BaseModel):
    """Base model for user answers with attempt and answer associations."""
    attempt_id: int
    answer_id: int


class UserAnswerCreate(UserAnswerBase):
    """Model for creating a user answer record."""
    pass


class UserAnswerRead(UserAnswerBase):
    """Model representing a user answer with submission timestamp."""
    submitted_at: datetime
