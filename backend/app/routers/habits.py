from datetime import datetime
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.config import Settings, get_settings
from backend.app.database import get_db
from backend.app.models import Habit, User
from backend.app.schemas import HabitCheckinResponse, HabitRead
from backend.app.security import get_current_user
from backend.app.services.rewards import apply_checkin_reward


router = APIRouter(prefix="/api/v1/habits", tags=["Habits"])


def current_time(settings: Settings) -> datetime:
    return datetime.now(ZoneInfo(settings.app_timezone))


def is_checked_in_today(last_check_in: datetime | None, settings: Settings) -> bool:
    if last_check_in is None:
        return False

    timezone = ZoneInfo(settings.app_timezone)
    if last_check_in.tzinfo is None:
        last_check_in = last_check_in.replace(tzinfo=timezone)

    today = current_time(settings).date()
    return last_check_in.astimezone(timezone).date() == today


def to_habit_read(habit: Habit, settings: Settings) -> HabitRead:
    return HabitRead(
        id=habit.id,
        title=habit.title,
        category=habit.category,
        last_check_in=habit.last_check_in,
        checked_in_today=is_checked_in_today(habit.last_check_in, settings),
    )


@router.get("", response_model=list[HabitRead])
def list_habits(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> list[HabitRead]:
    habits = db.scalars(
        select(Habit).where(Habit.user_id == current_user.id).order_by(Habit.id)
    ).all()
    return [to_habit_read(habit, settings) for habit in habits]


@router.post("/{habit_id}/checkin", response_model=HabitCheckinResponse)
def check_in_habit(
    habit_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> HabitCheckinResponse:
    habit = db.get(Habit, habit_id)
    if habit is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found.",
        )

    if habit.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to check in this habit.",
        )

    if is_checked_in_today(habit.last_check_in, settings):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Habit already checked in today.",
        )

    habit.last_check_in = current_time(settings)
    leveled_up = apply_checkin_reward(current_user)
    db.commit()
    db.refresh(current_user)
    db.refresh(habit)

    return HabitCheckinResponse(
        habit_id=habit.id,
        checked_in=True,
        current_exp=current_user.exp,
        current_gold=current_user.gold,
        current_level=current_user.level,
        leveled_up=leveled_up,
    )
