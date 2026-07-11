from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Unicode,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database import Base


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("level >= 1", name="ck_users_level_positive"),
        CheckConstraint("exp >= 0", name="ck_users_exp_nonnegative"),
        CheckConstraint("gold >= 0", name="ck_users_gold_nonnegative"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(Unicode(32), nullable=False)
    username_normalized: Mapped[str] = mapped_column(Unicode(32), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    exp: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    gold: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=now_utc,
        onupdate=now_utc,
    )

    habits: Mapped[list[Habit]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    checkins: Mapped[list[HabitCheckin]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Habit(Base):
    __tablename__ = "habits"
    __table_args__ = (
        CheckConstraint("streak_count >= 0", name="ck_habits_streak_nonnegative"),
        Index("ix_habits_user_active", "user_id", "is_archived"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(Unicode(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Unicode(500), nullable=True)
    category: Mapped[str | None] = mapped_column(Unicode(40), nullable=True)
    is_archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    streak_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_checkin_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=now_utc,
        onupdate=now_utc,
    )

    user: Mapped[User] = relationship(back_populates="habits")
    checkins: Mapped[list[HabitCheckin]] = relationship(
        back_populates="habit",
        cascade="all, delete-orphan",
    )


class HabitCheckin(Base):
    __tablename__ = "habit_checkins"
    __table_args__ = (
        UniqueConstraint("habit_id", "checkin_date", name="uq_habit_checkin_day"),
        Index("ix_habit_checkins_user_date", "user_id", "checkin_date"),
        CheckConstraint("exp_earned >= 0", name="ck_checkins_exp_nonnegative"),
        CheckConstraint("gold_earned >= 0", name="ck_checkins_gold_nonnegative"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    habit_id: Mapped[int] = mapped_column(ForeignKey("habits.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    checkin_date: Mapped[date] = mapped_column(Date, nullable=False)
    checked_in_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    exp_earned: Mapped[int] = mapped_column(Integer, nullable=False)
    gold_earned: Mapped[int] = mapped_column(Integer, nullable=False)

    habit: Mapped[Habit] = relationship(back_populates="checkins")
    user: Mapped[User] = relationship(back_populates="checkins")
