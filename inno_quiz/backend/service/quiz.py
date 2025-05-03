from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError

from backend.models import Quiz
from backend.domain.quiz import QuizCreate, QuizRead, Category


async def create_quiz_template(
    session: AsyncSession,
    quiz_data: QuizCreate,
    author_username: str,
    *,
    db: AsyncSession
) -> QuizRead:
    """
    Create a new quiz template and return the QuizRead domain object.
    """
    quiz = Quiz(
        quiz_id=uuid4(),
        name=quiz_data.name,
        category=quiz_data.category.name,
        author_username=author_username,
        is_submitted=quiz_data.is_submitted,
    )
    session.add(quiz)
    try:
        await session.commit()
        await session.refresh(quiz)
        return QuizRead(
            quiz_id=quiz.quiz_id,
            name=quiz.name,
            category=Category[quiz.category],
            is_submitted=quiz.is_submitted,
            author_username=quiz.author_username,
            created_at=quiz.created_at,
        )
    except SQLAlchemyError as e:
        await session.rollback()
        raise e


async def submit_quiz(session: AsyncSession, quiz_id: str) -> QuizRead:
    """
    Mark the quiz as submitted/ready for participan
    """
    result = await session.execute(select(Quiz).where(Quiz.quiz_id == quiz_id))
    quiz = result.scalar_one_or_none()
    if not quiz:
        raise ValueError("Quiz not found")
    quiz.is_submitted = True
    try:
        await session.commit()
        await session.refresh(quiz)
        return QuizRead(
            quiz_id=quiz.quiz_id,
            name=quiz.name,
            category=Category[quiz.category],
            is_submitted=quiz.is_submitted,
            author_username=quiz.author_username,
            created_at=quiz.created_at,
        )
    except SQLAlchemyError as e:
        await session.rollback()
        raise e
