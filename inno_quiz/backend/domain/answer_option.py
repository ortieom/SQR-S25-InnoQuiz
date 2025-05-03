from pydantic import BaseModel


class AnswerOptionBase(BaseModel):
    text: str
    is_correct: bool = False


class AnswerOptionCreate(AnswerOptionBase):
    question_id: int


class AnswerOptionRead(AnswerOptionBase):
    id: int
    question_id: int
