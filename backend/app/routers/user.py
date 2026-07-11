from typing import Annotated

from fastapi import APIRouter, Depends

from backend.app.models import User
from backend.app.schemas import UserProfile
from backend.app.security import get_current_user


router = APIRouter(prefix="/api/v1/user", tags=["User"])


@router.get("/profile", response_model=UserProfile)
def get_profile(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    return current_user
