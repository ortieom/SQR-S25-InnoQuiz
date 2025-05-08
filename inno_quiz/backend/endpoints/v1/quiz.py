from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.domain.quiz import QuizBase, QuizRead
from backend.service.quiz import create_quiz_template, submit_quiz
from backend.service import errors as service_errors
from backend.db import get_db

router = APIRouter(prefix="/quiz", tags=["quiz"])


@router.post(
    "/",
    response_model=QuizRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create Quiz",
    description="Creates a new quiz template with the given name and category"
)
def create_quiz(quiz_in: QuizBase, db: Session = Depends(get_db)):
    """
    Create a new quiz with basic information.

    Parameters:
        quiz_in (QuizBase): The basic quiz information including name and category
        db (Session): Database session

    Returns:
        QuizRead: The created quiz with ID and other details

    Raises:
        HTTPException: 400 if there are validation errors
    """
    author_username = "tester"  # TODO: replace it after implementing auth
    try:
        return create_quiz_template(quiz_in, author_username, db=db)
    except service_errors.ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.put(
    "/{quiz_id}/submit",
    response_model=QuizRead,
    summary="Submit Quiz",
    description="Finalizes a quiz, making it available for participants"
)
def submit_quiz_endpoint(quiz_id: UUID, db: Session = Depends(get_db)):
    """
    Submit a quiz, marking it as complete and ready for participants.

    Parameters:
        quiz_id (UUID): The ID of the quiz to submit
        db (Session): Database session

    Returns:
        QuizRead: The updated quiz with submission status

    Raises:
        HTTPException: 404 if the quiz is not found
    """
    try:
        return submit_quiz(quiz_id, db=db)
    except service_errors.QuizNotFoundError:
        raise HTTPException(status_code=404, detail="Quiz does not exist") from None
