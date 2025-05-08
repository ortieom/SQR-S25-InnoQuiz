from pydantic import BaseModel


class Token(BaseModel):
    """
    Model representing an authentication token.
    Used for API responses when a user successfully logs in.
    """
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    Model representing the data stored in a JWT token.
    Used internally for token validation and user identification.
    """
    username: str | None = None


class UserLogin(BaseModel):
    """
    Model for user login credentials.
    Used for authentication requests.
    """
    username: str
    password: str
