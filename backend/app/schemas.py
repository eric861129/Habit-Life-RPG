from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Credentials(BaseModel):
    username: str = Field(min_length=3, max_length=32)
    password: str = Field(min_length=10, max_length=128)

    @field_validator("username")
    @classmethod
    def normalize_display_username(cls, value: str) -> str:
        cleaned = value.strip()
        if len(cleaned) < 3:
            raise ValueError("Username must contain at least three visible characters.")
        return cleaned


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

    @field_validator("title")
    @classmethod
    def clean_title(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Habit title cannot be blank.")
        return cleaned

    @field_validator("description", "category")
    @classmethod
    def clean_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip() or None


class HabitUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    category: str | None = Field(default=None, max_length=40)
    is_archived: bool | None = None

    @field_validator("title")
    @classmethod
    def clean_title(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Habit title cannot be blank.")
        return cleaned

    @field_validator("description", "category")
    @classmethod
    def clean_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip() or None


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
