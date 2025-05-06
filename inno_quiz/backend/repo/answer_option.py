from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select

from .default import CRUDBase
from backend.models.answer_option import AnswerOption
from backend.domain.answer_option import AnswerOptionCreate, AnswerOptionRead


class AnswerOptionRepo(CRUDBase[AnswerOption, AnswerOptionCreate, AnswerOptionRead]):
    async def get_by_question_id_async(
        self, db: AsyncSession, *, question_id: int
    ) -> List[AnswerOptionRead]:
        """
        Get answer options for a specific question
        """
        query = select(AnswerOption).where(AnswerOption.question_id == question_id)
        result = await db.execute(query)
        options = result.scalars().all()
        return [AnswerOptionRead.model_validate(opt) for opt in options]

    def get_by_question_id(self, db: Session, question_id: str) -> List[AnswerOption]:
        """
        Get answer options for a specific question (sync version)
        """
        return (
            db.query(AnswerOption).filter(AnswerOption.question_id == question_id).all()
        )


answer_option = AnswerOptionRepo(AnswerOption)
