from .base import Base
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(64), primary_key=True)
    password: Mapped[str] = mapped_column(String(128), nullable=False)

    quizzes = relationship("Quiz", back_populates="author")
    attempts = relationship("UserAttempt", back_populates="user")
