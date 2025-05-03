from uuid import uuid4
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from backend.models.quiz import Quiz
from backend.domain.quiz import QuizCreate, QuizRead
from .default import CRUDBase


class QuizRepo(CRUDBase[Quiz, QuizCreate, QuizRead]):
    pass


quiz = QuizRepo(Quiz)
