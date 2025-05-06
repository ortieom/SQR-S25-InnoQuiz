from typing import List
from pydantic import BaseModel


class QuestionRequest(BaseModel):
    """Request model for creating a question"""

    text: str
    options: List[str]
    correct_options: List[int]


class QuestionResponse(BaseModel):
    """Response model for a question"""

    id: str
    text: str
    options: List[str]
    correct_options: List[int]
