from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.domain.question import QuestionCreate, QuestionRead
from backend.service.question import create_question, get_quiz_questions
from backend.service import errors as service_errors
from backend.db import get_db

router = APIRouter(prefix="/question", tags=["question"])


@router.post(
    "/", 
    response_model=QuestionRead, 
    status_code=status.HTTP_201_CREATED,
    summary="Create Question",
    description="Creates a new question for a quiz with answer options"
)
async def create_question_endpoint(
    question_in: QuestionCreate, db: AsyncSession = Depends(get_db)
):
    """
    Create a new question for a quiz with answer options.
    
    Parameters:
        question_in (QuestionCreate): The question data including text, quiz_id and answer options
        db (AsyncSession): Database session
    
    Returns:
        QuestionRead: The created question with ID and other details
    
    Raises:
        HTTPException: 404 if the quiz is not found
        HTTPException: 400 if there are validation errors
    """
    try:
        return await create_question(question_in, db=db)
    except service_errors.QuizNotFoundError:
        raise HTTPException(status_code=404, detail="Quiz not found") from None
    except service_errors.ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.get(
    "/quiz/{quiz_id}", 
    response_model=List[QuestionRead],
    summary="Get Quiz Questions",
    description="Retrieves all questions for a specific quiz"
)
async def get_quiz_questions_endpoint(
    quiz_id: UUID, db: AsyncSession = Depends(get_db)
):
    """
    Get all questions and their answer options for a specific quiz.
    
    Parameters:
        quiz_id (UUID): The ID of the quiz
        db (AsyncSession): Database session
    
    Returns:
        List[QuestionRead]: List of questions with their answer options
    
    Raises:
        HTTPException: 404 if the quiz is not found
        HTTPException: 400 if there are validation errors
    """
    try:
        return await get_quiz_questions(quiz_id, db=db)
    except service_errors.QuizNotFoundError:
        raise HTTPException(status_code=404, detail="Quiz not found") from None
    except service_errors.ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None
