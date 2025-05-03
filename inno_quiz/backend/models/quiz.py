import uuid

from sqlalchemy import String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone

from .base import Base


class Quiz(Base):
    __tablename__ = "quizzes"

    quiz_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    author_username: Mapped[str] = mapped_column(
        String(64), ForeignKey("users.username"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    is_submitted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(timezone.utc)
    )

    author = relationship("User", back_populates="quizzes")
    questions = relationship("Question", back_populates="quiz")
    attempts = relationship("UserAttempt", back_populates="quiz")
