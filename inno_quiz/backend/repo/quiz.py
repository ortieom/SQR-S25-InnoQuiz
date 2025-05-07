from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from backend.models.quiz import Quiz
from backend.domain.quiz import QuizCreate, QuizRead
from .default import CRUDBase


class QuizRepo(CRUDBase[Quiz, QuizCreate, QuizRead]):
    def get_by_id(self, db: Session, id: UUID) -> Optional[Quiz]:
        """
        Get a quiz by its ID
        """
        return db.query(Quiz).filter(Quiz.id == id).first()

    def get_by_author(self, db: Session, author_username: str) -> List[Quiz]:
        """
        Get all quizzes created by a specific user
        """
        return db.query(Quiz).filter(Quiz.author_username == author_username).all()


quiz = QuizRepo(Quiz)
