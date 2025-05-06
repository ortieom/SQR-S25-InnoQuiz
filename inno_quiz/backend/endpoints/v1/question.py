from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.domain.question import QuestionCreate, QuestionRead
from backend.service.question import create_question, get_quiz_questions
from backend.service import errors as service_errors
from backend.db import get_db

router = APIRouter(prefix="/question", tags=["question"])


@router.post("/", response_model=QuestionRead, status_code=status.HTTP_201_CREATED)
async def create_question_endpoint(
    question_in: QuestionCreate, db: AsyncSession = Depends(get_db)
):
    """
    Create a new question for a quiz
    """
    try:
        return await create_question(question_in, db=db)
    except service_errors.QuizNotFoundError:
        raise HTTPException(status_code=404, detail="Quiz not found") from None
    except service_errors.ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.get("/quiz/{quiz_id}", response_model=List[QuestionRead])
async def get_quiz_questions_endpoint(
    quiz_id: UUID, db: AsyncSession = Depends(get_db)
):
    """
    Get all questions for a specific quiz
    """
    try:
        return await get_quiz_questions(quiz_id, db=db)
    except service_errors.QuizNotFoundError:
        raise HTTPException(status_code=404, detail="Quiz not found") from None
    except service_errors.ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None
