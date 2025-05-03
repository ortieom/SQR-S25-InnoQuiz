from .default import CRUDBase
from backend.models.quiz import Quiz
from backend.domain.quiz import QuizCreate, QuizRead


class QuizRepo(CRUDBase[Quiz, QuizCreate, QuizRead]):
    pass


quiz = QuizRepo(Quiz)
