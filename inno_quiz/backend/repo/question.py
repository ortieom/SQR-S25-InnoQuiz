from uuid import UUID
from typing import List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from .default import CRUDBase
from backend.models.question import Question
from backend.models.answer_option import AnswerOption
from backend.domain.question import QuestionCreate, QuestionRead


class QuestionRepo(CRUDBase[Question, QuestionCreate, QuestionRead]):
    async def get_multi_by_quiz_id(
        self, db: AsyncSession, *, quiz_id: UUID
    ) -> List[QuestionRead]:
        """
        Get all questions for a specific quiz
        """
        query = select(Question).where(Question.quiz_id == quiz_id)
        result = await db.execute(query)
        questions = result.scalars().all()
        return [QuestionRead.model_validate(q) for q in questions]

    def get_by_quiz_id(self, db: Session, quiz_id: str) -> List[Question]:
        """
        Get all questions for a specific quiz (sync version)
        """
        return db.query(Question).filter(Question.quiz_id == quiz_id).all()

    def count_by_quiz_id(self, db: Session, quiz_id: str) -> int:
        """
        Count questions for a specific quiz
        """
        return (
            db.query(func.count(Question.id))
            .filter(Question.quiz_id == quiz_id)
            .scalar()
        )

    def create_with_options(
        self,
        db: Session,
        quiz_id: str,
        text: str,
        options: List[str],
        correct_options: List[int],
    ) -> Question:
        """
        Create a question with its answer options
        """
        # Create question
        question = Question(text=text, quiz_id=quiz_id)
        db.add(question)
        db.flush()  # Get the ID

        # Create options
        for i, option_text in enumerate(options):
            is_correct = i in correct_options
            option = AnswerOption(
                text=option_text, is_correct=is_correct, question_id=question.id
            )
            db.add(option)

        db.commit()
        db.refresh(question)
        return question


question = QuestionRepo(Question)
