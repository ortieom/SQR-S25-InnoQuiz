from typing import List
import json
from sqlalchemy.orm import Session

from .default import CRUDBase
from backend.models.user_answer import UserAnswer
from backend.domain.user_answer import UserAnswerCreate, UserAnswerRead


class UserAnswerRepo(CRUDBase[UserAnswer, UserAnswerCreate, UserAnswerRead]):
    def create(
        self,
        db: Session,
        *,
        attempt_id: str,
        question_id: str,
        selected_options: List[int]
    ) -> UserAnswer:
        """
        Create a user answer record
        """
        answer = UserAnswer(
            attempt_id=attempt_id,
            question_id=question_id,
            selected_options=json.dumps(selected_options),
        )
        db.add(answer)
        db.commit()
        db.refresh(answer)
        return answer


user_answer = UserAnswerRepo(UserAnswer)
