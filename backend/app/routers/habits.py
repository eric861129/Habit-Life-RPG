from datetime import datetime
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.config import Settings, get_settings
from backend.app.database import get_db
from backend.app.models import Habit, User
from backend.app.schemas import HabitRead
from backend.app.security import get_current_user


router = APIRouter(prefix="/api/v1/habits", tags=["Habits"])


def is_checked_in_today(last_check_in: datetime | None, settings: Settings) -> bool:
    if last_check_in is None:
        return False

    timezone = ZoneInfo(settings.app_timezone)
    if last_check_in.tzinfo is None:
        last_check_in = last_check_in.replace(tzinfo=timezone)

    today = datetime.now(timezone).date()
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
