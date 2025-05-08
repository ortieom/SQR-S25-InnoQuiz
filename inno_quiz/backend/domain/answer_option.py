from pydantic import BaseModel


class AnswerOptionBase(BaseModel):
    """
    Base model for answer options with text and correctness flag.
    Each question can have multiple answer options.
    """
    text: str
    is_correct: bool = False


class AnswerOptionCreate(AnswerOptionBase):
    """
    Model for creating a new answer option, extends AnswerOptionBase with question association.
    """
    question_id: int


class AnswerOptionRead(AnswerOptionBase):
    """
    Model representing an answer option with all fields including system-generated ID.
    Used for API responses.
    """
    id: int
    question_id: int
