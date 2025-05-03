from uuid import UUID

from pydantic import BaseModel


class QuestionBase(BaseModel):
    text: str


class QuestionCreate(QuestionBase):
    quiz_id: UUID


class QuestionRead(QuestionBase):
    question_id: int
    quiz_id: UUID
