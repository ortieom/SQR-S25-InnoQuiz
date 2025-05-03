

from backend.models.quiz import Quiz
from backend.domain.quiz import QuizCreate, QuizRead
from .default import CRUDBase


class QuizRepo(CRUDBase[Quiz, QuizCreate, QuizRead]):
    pass


quiz = QuizRepo(Quiz)
