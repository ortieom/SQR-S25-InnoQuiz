from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    quiz_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("quizzes.id"), nullable=False
    )
    text: Mapped[str] = mapped_column(String(512), nullable=False)

    quiz = relationship("Quiz", back_populates="questions")
    answer_options = relationship("AnswerOption", back_populates="question")
    user_answers = relationship("UserAnswer", back_populates="question")
