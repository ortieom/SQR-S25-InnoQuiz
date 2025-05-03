from models import Question, AnswerOption
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Dict, Any
import httpx


async def add_question_from_user(
    session: AsyncSession, quiz_id: str, question_data: Dict[str, Any]
) -> Question:
    """
    Add a question and its answer options from user input to the database.
    question_data should contain: {"text": str, "answers": List[{"text": str, "is_correct": bool}]}
    """
    question = Question(quiz_id=quiz_id, text=question_data["text"])
    session.add(question)
    await session.flush()  # To get question_id
    for ans in question_data["answers"]:
        answer = AnswerOption(
            question_id=question.question_id,
            text=ans["text"],
            is_correct=ans["is_correct"],
        )
        session.add(answer)
    try:
        await session.commit()
        await session.refresh(question)
        return question
    except SQLAlchemyError as e:
        await session.rollback()
        raise e


async def fetch_questions_for_quiz(
    session: AsyncSession, quiz_id: str
) -> List[Question]:
    """
    Fetch all questions for a given quiz.
    """
    result = await session.execute(select(Question).where(Question.quiz_id == quiz_id))
    return result.scalars().all()


async def load_questions_from_internet(
    session: AsyncSession, quiz_id: str, category: str, amount: int = 5
) -> List[Question]:
    """
    Fetch questions from OpenTDB and store them in the database for the quiz.
    """
    url = (
        f"https://opentdb.com/api.php?amount={amount}&category={category}&type=multiple"
    )
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        data = response.json()
        questions = []
        for item in data.get("results", []):
            q = Question(quiz_id=quiz_id, text=item["question"])
            session.add(q)
            await session.flush()
            # Correct answer
            session.add(
                AnswerOption(
                    question_id=q.question_id,
                    text=item["correct_answer"],
                    is_correct=True,
                )
            )
            # Incorrect answers
            for ans in item["incorrect_answers"]:
                session.add(
                    AnswerOption(question_id=q.question_id, text=ans, is_correct=False)
                )
            questions.append(q)
        try:
            await session.commit()
            for q in questions:
                await session.refresh(q)
            return questions
        except SQLAlchemyError as e:
            await session.rollback()
            raise e
