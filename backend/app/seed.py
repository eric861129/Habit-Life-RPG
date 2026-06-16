from sqlalchemy.orm import Session

from backend.app.models import Habit, User, now_taipei


DEMO_PASSWORD_HASH = "demo-password-hash-not-a-real-password"


def seed_demo_data(db: Session) -> None:
    existing = db.get(User, 1)
    if existing is not None:
        _refresh_daily_demo_habit(db)
        return

    user = User(
        id=1,
        username="arthur",
        password_hash=DEMO_PASSWORD_HASH,
        level=2,
        exp=120,
        gold=35,
        hp=86,
    )
    other_user = User(
        id=2,
        username="morgan",
        password_hash=DEMO_PASSWORD_HASH,
        level=1,
        exp=0,
        gold=0,
        hp=100,
    )
    db.add_all(
        [
            user,
            other_user,
            Habit(id=1, user=user, title="晨間 20 分鐘閱讀", category="Mind"),
            Habit(id=2, user=user, title="喝水 2000 ml", category="Body", last_check_in=now_taipei()),
            Habit(id=3, user=other_user, title="夜間伸展", category="Body"),
        ]
    )
    db.commit()


def _refresh_daily_demo_habit(db: Session) -> None:
    daily_habit = db.get(Habit, 2)
    if daily_habit is not None:
        daily_habit.last_check_in = now_taipei()
        db.commit()
