from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select

from .default import CRUDBase
from backend.models.answer_option import AnswerOption
from backend.domain.answer_option import AnswerOptionCreate, AnswerOptionRead


class AnswerOptionRepo(CRUDBase[AnswerOption, AnswerOptionCreate, AnswerOptionRead]):
    def get_by_question_id(
        self, db: Session, *, question_id: int
    ) -> List[AnswerOption]:
        """
        Get answer options for a specific question
        """
        query = select(AnswerOption).where(AnswerOption.question_id == question_id)
        result = db.execute(query)
        options = result.scalars().all()
        return options


answer_option = AnswerOptionRepo(AnswerOption)
