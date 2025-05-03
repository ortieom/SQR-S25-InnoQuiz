from pydantic import BaseModel


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    pass


class UserInfo(UserBase):
    """Model for returning authenticated user information"""
    is_authenticated: bool
    session_expires_in_minutes: int
