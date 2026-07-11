from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.config import Settings
from backend.app.models import Habit, User
from backend.app.seed import seed_demo_data


def test_demo_seed_is_explicit_and_idempotent(db_session: Session, settings: Settings):
    demo_settings = settings.model_copy(
        update={
            "demo_username": "book-demo",
            "demo_password": "PublicDemo!2026",
        }
    )

    seed_demo_data(db_session, demo_settings)
    seed_demo_data(db_session, demo_settings)

    assert db_session.scalar(select(func.count()).select_from(User)) == 1
    assert db_session.scalar(select(func.count()).select_from(Habit)) == 2
    user = db_session.scalar(select(User))
    assert user is not None
    assert user.username == "book-demo"
    assert user.password_hash != "PublicDemo!2026"
