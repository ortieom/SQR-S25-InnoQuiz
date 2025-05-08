from uuid import uuid4, UUID

from sqlalchemy.orm import Session

from backend.domain.question_request import QuestionRequest, QuestionResponse
from backend.domain.quiz_request import (
    QuizInfoResponse,
    LeaderboardResponse,
    LeaderboardEntry,
    QuizQuestionsResponse,
    QuizSubmissionRequest,
    QuizSubmissionResponse,
)
from backend.gateways.trivia import trivia_gateway
from backend.domain.quiz import QuizBase, QuizCreate, QuizRead
from backend.models import Quiz
from backend import repo
from . import errors


def create_quiz_template(
    quiz_data: QuizBase, author_username: str, *, db: Session
) -> Quiz:
    quiz = QuizCreate(
        id=uuid4(),
        name=quiz_data.name,
        category=quiz_data.category,
        author_username=author_username,
        is_submitted=quiz_data.is_submitted,
    )
    return repo.quiz.create(db, obj_in=quiz)


def submit_quiz(quiz_id: uuid4, *, db: Session) -> QuizRead:
    """
    Mark the quiz as submitted/ready for participan
    """
    quiz = repo.quiz.get_by_id(db, quiz_id)
    if quiz is None:
        raise errors.QuizNotFoundError()
    return repo.quiz.update(db, db_obj=quiz, obj_in={"is_submitted": True})


def add_question(
    quiz_id: str, question: QuestionRequest, db: Session
) -> QuestionResponse:
    """
    Add a question to a quiz
    """
    # Check if quiz exists
    quiz = repo.quiz.get_by_id(db, UUID(quiz_id))
    if quiz is None:
        raise errors.QuizNotFoundError()

    # Create question with options
    question_obj = repo.question.create_with_options(
        db=db,
        quiz_id=UUID(quiz_id),
        text=question.text,
        options=question.options,
        correct_options=question.correct_options,
    )

    # Get options separately since Question model doesn't have options field directly
    options = repo.answer_option.get_by_question_id(question_id=question_obj.id, db=db)

    return QuestionResponse(
        id=str(question_obj.id),
        text=question_obj.text,
        options=[opt.text for opt in options],
        correct_options=[i for i, opt in enumerate(options) if opt.is_correct],
    )


def load_external_questions(
    quiz_id: str, count: int, category: str, db: Session
) -> QuizQuestionsResponse:
    """
    Load questions from external API
    """
    # Check if quiz exists
    quiz = repo.quiz.get_by_id(db, UUID(quiz_id))
    if quiz is None:
        raise errors.QuizNotFoundError()

    # Use the existing trivia gateway to fetch questions
    trivia_questions = trivia_gateway.get_questions(
        amount=count, category=int(category) if category.isdigit() else None
    )

    # Save questions to database
    added_questions = []
    for q in trivia_questions:
        # Combine correct and incorrect answers
        options = [q.correct_answer] + q.incorrect_answers

        # The first option (index 0) is the correct answer
        correct_indices = [0]

        # Create a new question with options
        question_obj = repo.question.create_with_options(
            db=db,
            quiz_id=UUID(quiz_id),
            text=q.question,
            options=options,
            correct_options=correct_indices,
        )

        # Get options for the created question
        question_options = repo.answer_option.get_by_question_id(
            question_id=question_obj.id, db=db
        )

        added_questions.append(
            QuestionResponse(
                id=str(question_obj.id),
                text=question_obj.text,
                options=[opt.text for opt in question_options],
                correct_options=[
                    i for i, opt in enumerate(question_options) if opt.is_correct
                ],
            )
        )

    return QuizQuestionsResponse(
        quiz_id=quiz_id,
        name=quiz.name,
        category=str(quiz.category),
        questions=added_questions,
    )


def get_quiz_info(quiz_id: str, db: Session) -> QuizInfoResponse:
    """
    Get quiz information by ID
    """
    quiz = repo.quiz.get_by_id(db, UUID(quiz_id))
    if quiz is None:
        raise errors.QuizNotFoundError()

    question_count = repo.question.count_by_quiz_id(db, UUID(quiz_id))

    return QuizInfoResponse(
        quiz_id=str(quiz.id),
        name=quiz.name,
        category=str(quiz.category),
        author=quiz.author_username,
        creation_date=quiz.created_at,
        question_count=question_count,
    )


def get_leaderboard(quiz_id: str, db: Session) -> LeaderboardResponse:
    """
    Get quiz leaderboard
    """
    quiz = repo.quiz.get_by_id(db, UUID(quiz_id))
    if quiz is None:
        raise errors.QuizNotFoundError()

    # Get attempt records for this quiz
    attempts = repo.user_attempt.get_by_quiz_id(db, UUID(quiz_id))

    entries = [
        LeaderboardEntry(
            username=attempt.user.username,
            score=attempt.score,
            completion_time=attempt.completion_time,
            date=attempt.started_at,
        )
        for attempt in attempts
    ]

    # Sort entries by score (desc) and completion time (asc)
    entries.sort(key=lambda e: (-e.score, e.completion_time))

    return LeaderboardResponse(
        quiz_id=str(quiz.id), quiz_name=quiz.name, entries=entries
    )


def get_quiz_questions(quiz_id: str, db: Session) -> QuizQuestionsResponse:
    """
    Get all questions for a quiz
    """
    quiz = repo.quiz.get_by_id(db, UUID(quiz_id))
    if quiz is None:
        raise errors.QuizNotFoundError()

    questions = repo.question.get_by_quiz_id(db, UUID(quiz_id))

    question_responses = []
    for q in questions:
        options = repo.answer_option.get_by_question_id(question_id=q.id, db=db)
        question_responses.append(
            QuestionResponse(
                id=str(q.id),
                text=q.text,
                options=[opt.text for opt in options],
                correct_options=[i for i, opt in enumerate(options) if opt.is_correct],
            )
        )

    return QuizQuestionsResponse(
        quiz_id=str(quiz.id),
        name=quiz.name,
        category=str(quiz.category),
        questions=question_responses,
    )


def submit_quiz_answers(
    request: QuizSubmissionRequest, db: Session
) -> QuizSubmissionResponse:
    """
    Submit answers for a quiz
    """
    quiz = repo.quiz.get_by_id(db, UUID(request.quiz_id))
    if quiz is None:
        raise errors.QuizNotFoundError()

    # Validate user
    user = repo.user.get_by_username(db, request.user_id)
    if user is None:
        raise errors.UserNotFoundError()

    # Calculate score
    total_questions = repo.question.count_by_quiz_id(db, UUID(request.quiz_id))
    correct_count = 0

    for answer in request.answers:
        # Try to convert question_id to UUID, but handle case where it might be a different format
        try:
            question_uuid = UUID(answer.question_id)
            question = repo.question.get_by_id(db, question_uuid)
        except ValueError:
            # If not a UUID, try to get it directly (might be a simple ID)
            question = repo.question.get_by_id(db, answer.question_id)

        if question is None:
            continue

        options = repo.answer_option.get_by_question_id(question_id=question.id, db=db)
        correct_indices = [i for i, opt in enumerate(options) if opt.is_correct]

        # Check if answered correctly (selected options match correct options exactly)
        if sorted(answer.selected_options) == sorted(correct_indices):
            correct_count += 1

    # Create user attempt record
    attempt = repo.user_attempt.create(
        db=db,
        username=user.username,
        quiz_id=UUID(request.quiz_id),
        score=correct_count,
        completion_time=request.completion_time,
    )

    # Save individual answers
    for answer in request.answers:
        # Try to convert question_id to UUID, but handle case where it might be a different format
        try:
            question_id = UUID(answer.question_id)
        except ValueError:
            question_id = answer.question_id

        repo.user_answer.create(
            db=db,
            attempt_id=attempt.id,
            question_id=question_id,
            selected_options=answer.selected_options,
        )

    # Calculate rank if possible
    rank = None
    attempts = repo.user_attempt.get_by_quiz_id(db, UUID(request.quiz_id))
    if attempts:
        # Sort by score (desc) and completion time (asc)
        sorted_attempts = sorted(attempts, key=lambda a: (-a.score, a.completion_time))
        for i, a in enumerate(sorted_attempts):
            if a.id == attempt.id:
                rank = i + 1
                break

    return QuizSubmissionResponse(
        quiz_id=str(quiz.id),
        score=correct_count,
        total=total_questions,
        completion_time=request.completion_time,
        rank=rank,
    )
