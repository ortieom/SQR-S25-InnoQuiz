from typing import List
from pydantic import BaseModel


class TriviaQuestion(BaseModel):
    category: str
    type: str
    difficulty: str
    question: str
    correct_answer: str
    incorrect_answers: List[str] 