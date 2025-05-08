from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.domain.question_request import QuestionRequest, QuestionResponse
from backend.domain.quiz import QuizBase, QuizRead
from backend.domain.quiz_request import (
    QuizInfoResponse,
    LeaderboardResponse,
    QuizQuestionsResponse,
    QuizSubmissionRequest,
    QuizSubmissionResponse,
)
from backend.service import quiz as quiz_service, errors as service_errors
from backend.db import get_db
from backend.deps import get_current_user_from_cookie
from backend.models.user import User

router = APIRouter(
    prefix="/quiz",
    tags=["quiz"],
    dependencies=[Depends(get_current_user_from_cookie)],
)


@router.post("/", response_model=QuizRead, status_code=status.HTTP_201_CREATED)
def create_quiz(
    quiz_in: QuizBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    try:
        return quiz_service.create_quiz_template(quiz_in, current_user.username, db=db)
    except service_errors.ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.put("/{quiz_id}/submit", response_model=QuizRead)
def submit_quiz_endpoint(
    quiz_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    try:
        return quiz_service.submit_quiz(quiz_id, db=db)
    except service_errors.QuizNotFoundError:
        raise HTTPException(status_code=404, detail="Quiz does not exist") from None


@router.post("/{quiz_id}/questions", response_model=QuestionResponse)
def add_question(
    quiz_id: str,
    question: QuestionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    """
    Add a question to a quiz
    """
    try:
        return quiz_service.add_question(quiz_id, question, db=db)
    except service_errors.QuizNotFoundError:
        raise HTTPException(status_code=404, detail="Quiz not found") from None
    except service_errors.ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.get("/{quiz_id}/load_questions", response_model=QuizQuestionsResponse)
def load_external_questions(
    quiz_id: str,
    count: int,
    category: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    """
    Load questions from external API
    """
    try:
        return quiz_service.load_external_questions(quiz_id, count, category, db=db)
    except service_errors.QuizNotFoundError:
        raise HTTPException(status_code=404, detail="Quiz not found") from None
    except service_errors.ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"External API error: {str(e)}"
        ) from None


@router.get("/{quiz_id}", response_model=QuizInfoResponse)
def get_quiz_info(
    quiz_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    """
    Get quiz information by ID
    """
    try:
        return quiz_service.get_quiz_info(quiz_id, db=db)
    except service_errors.QuizNotFoundError:
        raise HTTPException(status_code=404, detail="Quiz not found") from None
    except service_errors.ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.get("/{quiz_id}/leaderboard", response_model=LeaderboardResponse)
def get_leaderboard(
    quiz_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    """
    Get quiz leaderboard
    """
    try:
        return quiz_service.get_leaderboard(quiz_id, db=db)
    except service_errors.QuizNotFoundError:
        raise HTTPException(status_code=404, detail="Quiz not found") from None
    except service_errors.ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.get("/{quiz_id}/questions", response_model=QuizQuestionsResponse)
def get_quiz_questions(
    quiz_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    """
    Get all questions for a quiz
    """
    try:
        return quiz_service.get_quiz_questions(quiz_id, db=db)
    except service_errors.QuizNotFoundError:
        raise HTTPException(status_code=404, detail="Quiz not found") from None
    except service_errors.ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.post("/{quiz_id}/answers", response_model=QuizSubmissionResponse)
def submit_quiz_answers(
    request: QuizSubmissionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    """
    Submit answers for a quiz
    """
    # Set the user_id from the authenticated user
    request.user_id = current_user.username

    try:
        return quiz_service.submit_quiz_answers(request, db=db)
    except service_errors.QuizNotFoundError:
        raise HTTPException(status_code=404, detail="Quiz not found") from None
    except service_errors.UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found") from None
    except service_errors.ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None
