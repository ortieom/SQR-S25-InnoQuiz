from uuid import UUID
from datetime import datetime

from pydantic import BaseModel


class UserAttemptBase(BaseModel):
    """
    Base model for quiz attempts by users.
    Represents a user starting a quiz.
    """
    username: str
    quiz_id: UUID


class UserAttemptCreate(UserAttemptBase):
    """
    Model for creating a user attempt record.
    Currently identical to the base model.
    """
    pass


class UserAttemptRead(UserAttemptBase):
    """
    Model representing a user attempt with system-generated ID and timestamp.
    Used for API responses.
    """
    id: int
    started_at: datetime
