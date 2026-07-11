from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.config import Settings, get_settings
from backend.app.database import get_db
from backend.app.models import User
from backend.app.schemas import Credentials, TokenResponse
from backend.app.security import (
    create_access_token,
    hash_password,
    normalize_username,
    verify_password,
)


router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"description": "Username is already registered."}},
)
def register(
    credentials: Credentials,
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> TokenResponse:
    normalized = normalize_username(credentials.username)
    if db.scalar(select(User).where(User.username_normalized == normalized)) is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Username is already registered.")

    user = User(
        username=credentials.username,
        username_normalized=normalized,
        password_hash=hash_password(credentials.password),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Username is already registered.") from error
    db.refresh(user)
    return TokenResponse(access_token=create_access_token(str(user.id), settings))


@router.post(
    "/login",
    response_model=TokenResponse,
    responses={401: {"description": "Invalid username or password."}},
)
def login(
    credentials: Credentials,
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> TokenResponse:
    user = db.scalar(
        select(User).where(User.username_normalized == normalize_username(credentials.username))
    )
    if user is None or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenResponse(access_token=create_access_token(str(user.id), settings))
