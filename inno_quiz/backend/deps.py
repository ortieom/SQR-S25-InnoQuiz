from fastapi import Cookie, Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from backend.auth.jwt import TokenData
from backend.config import settings
from backend.db import get_db
from backend.models.user import User
from backend.repo.user import get_user_by_username


def get_current_user_from_cookie(
    access_token: str = Cookie(None, alias="access_token"),
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current user from the JWT token in the cookie
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not access_token:
        raise credentials_exception

    # Remove 'Bearer ' if it's in the token
    if access_token.startswith("Bearer "):
        access_token = access_token[7:]

    try:
        payload = jwt.decode(
            access_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    # Ensure username is not None before using it
    if token_data.username is None:
        raise credentials_exception

    user = get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception

    return user
