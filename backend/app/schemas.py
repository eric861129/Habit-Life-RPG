from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserProfile(BaseModel):
    id: int
    username: str
    level: int
    exp: int
    gold: int
    hp: int

    model_config = ConfigDict(from_attributes=True)


class HabitRead(BaseModel):
    id: int
    title: str
    category: str | None
    last_check_in: datetime | None
    checked_in_today: bool


class HabitCheckinResponse(BaseModel):
    habit_id: int
    checked_in: bool
    current_exp: int
    current_gold: int
    current_level: int
    leveled_up: bool
