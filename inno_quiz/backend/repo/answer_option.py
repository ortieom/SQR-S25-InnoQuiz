from .default import CRUDBase
from backend.models.answer_option import AnswerOption
from backend.domain.answer_option import AnswerOptionCreate, AnswerOptionRead


class AnswerOptionRepo(CRUDBase[AnswerOption, AnswerOptionCreate, AnswerOptionRead]):
    pass
