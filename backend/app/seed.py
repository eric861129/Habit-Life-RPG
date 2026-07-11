from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.config import Settings, get_settings
from backend.app.database import SessionLocal
from backend.app.models import Habit, User
from backend.app.security import hash_password, normalize_username


def seed_demo_data(db: Session, settings: Settings) -> None:
    if settings.demo_password.startswith("replace-with-"):
        raise ValueError("Replace HLR_DEMO_PASSWORD before seeding demo data.")

    normalized = normalize_username(settings.demo_username)
    user = db.scalar(select(User).where(User.username_normalized == normalized))
    if user is None:
        user = User(
            username=settings.demo_username,
            username_normalized=normalized,
            password_hash=hash_password(settings.demo_password),
        )
        db.add(user)
        db.flush()
    else:
        user.password_hash = hash_password(settings.demo_password)

    if not user.habits:
        db.add_all(
            [
                Habit(user=user, title="閱讀 20 分鐘", category="學習"),
                Habit(user=user, title="散步 15 分鐘", category="健康"),
            ]
        )
    db.commit()


def main() -> None:
    settings = get_settings()
    with SessionLocal() as db:
        seed_demo_data(db, settings)
    print("Demo account is ready.")


if __name__ == "__main__":
    main()
