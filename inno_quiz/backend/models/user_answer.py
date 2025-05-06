from datetime import datetime, timezone
import json

from sqlalchemy import Integer, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class UserAnswer(Base):
    __tablename__ = "user_answers"

    attempt_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_attempts.id"), primary_key=True
    )
    question_id: Mapped[str] = mapped_column(
        String, ForeignKey("questions.id"), primary_key=True
    )
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(timezone.utc)
    )
    selected_options: Mapped[str] = mapped_column(String, nullable=False, default="[]")

    attempt = relationship("UserAttempt", back_populates="answers")
    question = relationship("Question", back_populates="user_answers")

    def get_selected_options(self) -> list[int]:
        """Convert the stored JSON string to a list of integers."""
        return json.loads(self.selected_options)

    def set_selected_options(self, options: list[int]) -> None:
        """Convert a list of integers to a JSON string for storage."""
        self.selected_options = json.dumps(options)
