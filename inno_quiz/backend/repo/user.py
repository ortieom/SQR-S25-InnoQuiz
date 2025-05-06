from typing import Optional

from sqlalchemy.orm import Session

from .default import CRUDBase
from backend.models.user import User
from backend.domain.user import UserCreate, UserRead


class UserRepo(CRUDBase[User, UserCreate, UserRead]):
    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """
        Get a user by username.
        """
        return get_user_by_username(db, username)


user = UserRepo(User)


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """
    Get a user by username.
    """
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, username: str, hashed_password: str) -> User:
    """
    Create a new user.
    """
    user = User(username=username, password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def verify_username_unique(db: Session, username: str) -> bool:
    """
    Check if username is already taken.
    """
    existing_user = get_user_by_username(db, username)
    return existing_user is None
