from uuid import UUID
from datetime import datetime

from pydantic import BaseModel


class UserAttemptBase(BaseModel):
    username: str
    quiz_id: UUID


class UserAttemptCreate(UserAttemptBase):
    pass


class UserAttemptRead(UserAttemptBase):
    attempt_id: int
    started_at: datetime
