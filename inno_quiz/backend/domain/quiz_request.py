from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from .question_request import QuestionResponse


class QuizInfoRequest(BaseModel):
    """Request model for getting quiz info"""

    quiz_id: str


class QuizInfoResponse(BaseModel):
    """Response model for quiz info"""

    quiz_id: str
    name: str
    category: str
    author: str
    creation_date: datetime
    question_count: int


class LeaderboardEntry(BaseModel):
    """Model for leaderboard entry"""

    username: str
    score: int
    completion_time: float
    date: datetime


class LeaderboardResponse(BaseModel):
    """Response model for leaderboard"""

    quiz_id: str
    quiz_name: str
    entries: List[LeaderboardEntry]


class QuizQuestionsResponse(BaseModel):
    """Response model for quiz questions"""

    quiz_id: str
    name: str
    category: str
    questions: List[QuestionResponse]


class QuizCreateRequest(BaseModel):
    """Request model for creating a quiz"""

    name: str
    category: str
    author_id: str


class QuizCreateResponse(BaseModel):
    """Response model for quiz creation"""

    quiz_id: str
    name: str
    success: bool = True


class QuizAnswerRequest(BaseModel):
    """Request model for a single quiz answer"""

    question_id: str
    selected_options: List[int]


class QuizSubmissionRequest(BaseModel):
    """Request model for submitting quiz answers"""

    quiz_id: str
    user_id: str
    answers: List[QuizAnswerRequest]
    completion_time: float


class QuizSubmissionResponse(BaseModel):
    """Response model for quiz submission"""

    quiz_id: str
    score: int
    total: int
    completion_time: float
    rank: Optional[int] = None
