from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from backend.domain.quiz import QuizBase, QuizCreate, QuizRead
from backend.models import Quiz
from backend import repo
from . import errors


def create_quiz_template(
    quiz_data: QuizBase, author_username: str, *, db: AsyncSession
) -> Quiz:
    quiz = QuizCreate(
        id=uuid4(),
        name=quiz_data.name,
        category=quiz_data.category,
        author_username=author_username,
        is_submitted=quiz_data.is_submitted,
    )
    return repo.quiz.create(db, obj_in=quiz)


def submit_quiz(quiz_id: uuid4, *, db: AsyncSession) -> QuizRead:
    """
    Mark the quiz as submitted/ready for participan
    """
    quiz = repo.quiz.get_by_id(db, quiz_id)
    if quiz is None:
        raise errors.QuizNotFoundError()
    return repo.quiz.update(db, db_obj=quiz, obj_in={"is_submitted": True})
