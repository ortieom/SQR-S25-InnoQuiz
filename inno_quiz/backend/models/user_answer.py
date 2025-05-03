from datetime import datetime, timezone

from sqlalchemy import Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class UserAnswer(Base):
    __tablename__ = "user_answers"

    attempt_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_attempts.attempt_id"), primary_key=True
    )
    answer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("answer_options.answer_id"), primary_key=True
    )
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(timezone.utc)
    )

    attempt = relationship("UserAttempt", back_populates="answers")
    answer_option = relationship("AnswerOption", back_populates="user_answers")
