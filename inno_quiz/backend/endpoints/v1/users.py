from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

# Modified imports for running from backend directory
from auth import create_access_token, get_password_hash, verify_password
from config import settings
from db import get_db
from domain.auth import Token
from domain.user import UserCreate, UserRead, UserInfo
from models.user import User
from repo.user import create_user, get_user_by_username, verify_username_unique
from deps import get_current_user_from_cookie

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/create", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(
    user_create: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new user with the provided username and password.
    """
    # Check if username already exists
    is_unique = verify_username_unique(db, user_create.username)
    if not is_unique:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Hash the password
    hashed_password = get_password_hash(user_create.password)

    # Create new user
    user = create_user(db, user_create.username, hashed_password)

    return user


@router.post("/login", response_model=Token)
def login_for_access_token(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    """
    Authenticate a user and return a JWT token for further API access.
    """
    # Validate user credentials
    user = get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )

    # Set token in cookie
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserInfo)
def get_user_me(current_user: User = Depends(get_current_user_from_cookie)):
    """
    Get information about the currently authenticated user.
    This endpoint requires authentication.
    """
    return {
        "username": current_user.username,
        "is_authenticated": True,
        "session_expires_in_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES
    }
