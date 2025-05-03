from .default import CRUDBase
from backend.models.question import Question
from backend.domain.question import QuestionCreate, QuestionRead


class QuestionRepo(CRUDBase[Question, QuestionCreate, QuestionRead]):
    pass
