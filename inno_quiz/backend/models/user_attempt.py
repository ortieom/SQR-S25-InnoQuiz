from datetime import datetime, timezone

from sqlalchemy import Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class UserAttempt(Base):
    __tablename__ = "user_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(
        String(64), ForeignKey("users.username"), nullable=False
    )
    quiz_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("quizzes.id"), nullable=False
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(timezone.utc)
    )
    score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    completion_time: Mapped[float] = mapped_column(Float, nullable=True)

    user = relationship("User", back_populates="attempts")
    quiz = relationship("Quiz", back_populates="attempts")
    answers = relationship("UserAnswer", back_populates="attempt")
