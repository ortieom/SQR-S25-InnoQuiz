from uuid import UUID
from typing import List

from sqlalchemy.orm import Session

from backend.domain.question import QuestionCreate, QuestionRead
from backend import repo
from . import errors


def create_question(question_data: QuestionCreate, *, db: Session) -> QuestionRead:
    """
    Create a new question for a quiz
    """
    # Verify quiz exists
    quiz = repo.quiz.get_by_id(db, question_data.quiz_id)
    if quiz is None:
        raise errors.QuizNotFoundError()

    return repo.question.create(db, obj_in=question_data)


def get_quiz_questions(quiz_id: UUID, *, db: Session) -> List[QuestionRead]:
    """
    Get all questions for a specific quiz
    """
    # Verify quiz exists
    quiz = repo.quiz.get_by_id(db, quiz_id)
    if quiz is None:
        raise errors.QuizNotFoundError()

    return repo.question.get_multi_by_quiz_id(db, quiz_id=quiz_id)
