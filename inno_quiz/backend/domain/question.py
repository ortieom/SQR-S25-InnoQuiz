from pydantic import BaseModel
from uuid import UUID


class QuestionBase(BaseModel):
    text: str


class QuestionCreate(QuestionBase):
    quiz_id: UUID


class QuestionRead(QuestionBase):
    question_id: int
    quiz_id: UUID
