from uuid import UUID
from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class Category(Enum):
    """Quiz category enumeration based on Open Trivia DB categories."""
    undefined = None
    general_knowledge = 9
    entertainment_books = 10
    entertainment_film = 11
    entertainment_music = 12
    entertainment_music_and_theatres = 13
    entertainment_television = 14
    entertainment_video_games = 15
    entertainment_board_games = 16
    science_and_nature = 17
    science_computers = 18
    science_mathematics = 19
    mythology = 20
    sports = 21
    geography = 22
    history = 23
    politics = 24
    art = 25
    celebrities = 26
    animals = 27
    vehicles = 28
    entertainment_comics = 29
    science_gadgets = 30
    entertainment_japanese_anime_and_manga = 31
    entertainment_cartoons_and_animations = 32


class QuizBase(BaseModel):
    """Base model for quiz data with essential fields."""
    name: str
    category: int
    is_submitted: bool = False


class QuizCreate(QuizBase):
    """Model for creating a new quiz, extends QuizBase with author information."""
    author_username: str


class QuizRead(QuizBase):
    """
    Model representing a quiz with all fields including system-generated ones.
    Used for API responses.
    """
    id: UUID
    author_username: str
    created_at: datetime
