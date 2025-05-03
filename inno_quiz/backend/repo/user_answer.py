from .default import CRUDBase
from backend.models.user_answer import UserAnswer
from backend.domain.user_answer import UserAnswerCreate, UserAnswerRead


class UserAnswerRepo(CRUDBase[UserAnswer, UserAnswerCreate, UserAnswerRead]):
    pass
