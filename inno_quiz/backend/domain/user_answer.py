from pydantic import BaseModel
from datetime import datetime


class UserAnswerBase(BaseModel):
    attempt_id: int
    answer_id: int


class UserAnswerCreate(UserAnswerBase):
    pass


class UserAnswerRead(UserAnswerBase):
    submitted_at: datetime
