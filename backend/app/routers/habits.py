from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.config import Settings, get_settings
from backend.app.database import get_db
from backend.app.models import Habit, HabitCheckin, User
from backend.app.schemas import CheckinRead, HabitCreate, HabitRead, HabitUpdate
from backend.app.security import get_current_user
from backend.app.services import checkins as checkin_service
from backend.app.services.rewards import apply_checkin_reward


router = APIRouter(prefix="/api/v1/habits", tags=["Habits"])


def owned_habit_or_404(db: Session, user_id: int, habit_id: int) -> Habit:
    habit = db.scalar(select(Habit).where(Habit.id == habit_id, Habit.user_id == user_id))
    if habit is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Habit not found.")
    return habit


def to_habit_read(habit: Habit, today) -> HabitRead:
    return HabitRead(
        id=habit.id,
        title=habit.title,
        description=habit.description,
        category=habit.category,
        is_archived=habit.is_archived,
        streak_count=habit.streak_count,
        last_checkin_date=habit.last_checkin_date,
        checked_in_today=habit.last_checkin_date == today,
    )


@router.get("", response_model=list[HabitRead])
def list_habits(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
    include_archived: Annotated[bool, Query()] = False,
) -> list[HabitRead]:
    query = select(Habit).where(Habit.user_id == current_user.id)
    if not include_archived:
        query = query.where(Habit.is_archived.is_(False))
    habits = db.scalars(query.order_by(Habit.created_at, Habit.id)).all()
    today = checkin_service.today_in_timezone(settings)
    return [to_habit_read(habit, today) for habit in habits]


@router.post("", response_model=HabitRead, status_code=status.HTTP_201_CREATED)
def create_habit(
    payload: HabitCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> HabitRead:
    habit = Habit(user_id=current_user.id, **payload.model_dump())
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return to_habit_read(habit, checkin_service.today_in_timezone(settings))


@router.get("/{habit_id}", response_model=HabitRead)
def get_habit(
    habit_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> HabitRead:
    habit = owned_habit_or_404(db, current_user.id, habit_id)
    return to_habit_read(habit, checkin_service.today_in_timezone(settings))


@router.patch("/{habit_id}", response_model=HabitRead)
def update_habit(
    habit_id: int,
    payload: HabitUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> HabitRead:
    habit = owned_habit_or_404(db, current_user.id, habit_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        if field == "title" and value is None:
            continue
        setattr(habit, field, value)
    db.commit()
    db.refresh(habit)
    return to_habit_read(habit, checkin_service.today_in_timezone(settings))


@router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
def archive_habit(
    habit_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Response:
    habit = owned_habit_or_404(db, current_user.id, habit_id)
    habit.is_archived = True
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{habit_id}/checkins",
    response_model=CheckinRead,
    status_code=status.HTTP_201_CREATED,
)
def check_in_habit(
    habit_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> CheckinRead:
    habit = owned_habit_or_404(db, current_user.id, habit_id)
    if habit.is_archived:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Habit not found.")

    today = checkin_service.today_in_timezone(settings)
    if habit.last_checkin_date == today:
        raise HTTPException(status.HTTP_409_CONFLICT, "Habit already checked in today.")

    continuation = checkin_service.next_streak(habit.last_checkin_date, today)
    habit.streak_count = habit.streak_count + 1 if continuation else 1
    habit.last_checkin_date = today
    reward = apply_checkin_reward(current_user)
    checkin = HabitCheckin(
        habit_id=habit.id,
        user_id=current_user.id,
        checkin_date=today,
        exp_earned=reward.exp_earned,
        gold_earned=reward.gold_earned,
    )
    db.add(checkin)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Habit already checked in today.",
        ) from error
    db.refresh(checkin)
    db.refresh(habit)
    db.refresh(current_user)
    return CheckinRead(
        id=checkin.id,
        habit_id=habit.id,
        checkin_date=checkin.checkin_date,
        checked_in_at=checkin.checked_in_at,
        exp_earned=checkin.exp_earned,
        gold_earned=checkin.gold_earned,
        streak_count=habit.streak_count,
        current_exp=current_user.exp,
        current_gold=current_user.gold,
        current_level=current_user.level,
        leveled_up=reward.leveled_up,
    )
