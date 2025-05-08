from pydantic import BaseModel


class UserBase(BaseModel):
    """Base model for user data with username."""
    username: str


class UserCreate(UserBase):
    """Model for creating a new user, extends UserBase with password."""
    password: str


class UserRead(UserBase):
    """
    Model for returning user data in API responses.
    Currently only includes username from the base model.
    """
    pass


class UserInfo(UserBase):
    """
    Model for returning authenticated user information.
    Includes authentication status and session expiration details.
    """
    is_authenticated: bool
    session_expires_in_minutes: int
