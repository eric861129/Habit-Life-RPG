from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class Credentials(BaseModel):
    username: str = Field(min_length=3, max_length=32)
    password: str = Field(min_length=10, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserProfile(BaseModel):
    id: int
    username: str
    level: int
    exp: int
    gold: int

    model_config = ConfigDict(from_attributes=True)


class HabitCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    category: str | None = Field(default=None, max_length=40)


class HabitUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    category: str | None = Field(default=None, max_length=40)
    is_archived: bool | None = None


class HabitRead(BaseModel):
    id: int
    title: str
    description: str | None
    category: str | None
    is_archived: bool
    streak_count: int
    last_checkin_date: date | None
    checked_in_today: bool

    model_config = ConfigDict(from_attributes=True)


class CheckinRead(BaseModel):
    id: int
    habit_id: int
    checkin_date: date
    checked_in_at: datetime
    exp_earned: int
    gold_earned: int
    streak_count: int
    current_exp: int
    current_gold: int
    current_level: int
    leveled_up: bool
