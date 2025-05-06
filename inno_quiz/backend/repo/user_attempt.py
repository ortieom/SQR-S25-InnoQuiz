from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .default import CRUDBase
from backend.models.user_attempt import UserAttempt
from backend.domain.user_attempt import UserAttemptCreate, UserAttemptRead


class UserAttemptRepo(CRUDBase[UserAttempt, UserAttemptCreate, UserAttemptRead]):
    async def get_by_quiz_id_async(
        self, db: AsyncSession, *, quiz_id: str
    ) -> List[UserAttemptRead]:
        """
        Get all user attempts for a specific quiz
        """
        query = select(UserAttempt).where(UserAttempt.quiz_id == quiz_id)
        result = await db.execute(query)
        attempts = result.scalars().all()
        return [UserAttemptRead.model_validate(a) for a in attempts]

    def get_by_quiz_id(self, db: Session, quiz_id: str) -> List[UserAttempt]:
        """
        Get all user attempts for a specific quiz (sync version)
        """
        return db.query(UserAttempt).filter(UserAttempt.quiz_id == quiz_id).all()

    def create(
        self,
        db: Session,
        *,
        username: str,
        quiz_id: str,
        score: int,
        completion_time: float
    ) -> UserAttempt:
        """
        Create a user attempt record
        """
        attempt = UserAttempt(
            username=username,
            quiz_id=quiz_id,
            score=score,
            completion_time=completion_time,
        )
        db.add(attempt)
        db.commit()
        db.refresh(attempt)
        return attempt


user_attempt = UserAttemptRepo(UserAttempt)
