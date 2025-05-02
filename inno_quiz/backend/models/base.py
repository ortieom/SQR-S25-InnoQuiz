"""
SQLAlchemy model basic class with whole app metadata
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase


class Base(AsyncAttrs, DeclarativeBase):
    """
    Base SQLAlchemy model class
    """
