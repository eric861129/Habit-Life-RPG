from collections.abc import Generator
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.app.config import Settings, get_settings
from backend.app.database import Base, get_db
from backend.app.main import create_app
from backend.app.models import Habit, User
from backend.app.routers import habits as habits_router


AUTH_HEADERS = {"Authorization": "Bearer local-dev-token"}
TAIPEI = ZoneInfo("Asia/Taipei")


@pytest.fixture
def fixed_now() -> datetime:
    return datetime(2026, 6, 16, 9, 0, 0, tzinfo=TAIPEI)


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return AUTH_HEADERS.copy()


@pytest.fixture
def db_session(tmp_path, fixed_now: datetime) -> Generator[Session, None, None]:
    database_url = f"sqlite:///{tmp_path / 'habit_life_rpg_test.db'}"
    engine = create_engine(database_url, connect_args={"check_same_thread": False}, future=True)
    testing_session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

    Base.metadata.create_all(bind=engine)
    with testing_session_local() as session:
        seed_test_data(session, fixed_now)
        yield session

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def client(
    db_session: Session,
    fixed_now: datetime,
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[TestClient, None, None]:
    app = create_app(enable_startup_seed=False)

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    def override_get_settings() -> Settings:
        return Settings(
            DATABASE_URL="sqlite:///./test-only.db",
            HLR_DEV_AUTH_TOKEN="local-dev-token",
            HLR_DEMO_USER_ID=1,
            HLR_APP_TIMEZONE="Asia/Taipei",
        )

    monkeypatch.setattr(habits_router, "current_time", lambda settings: fixed_now)
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_settings] = override_get_settings

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def seed_test_data(db: Session, fixed_now: datetime) -> None:
    user = User(
        id=1,
        username="arthur",
        password_hash="test-password-hash",
        level=2,
        exp=120,
        gold=35,
        hp=86,
    )
    other_user = User(
        id=2,
        username="morgan",
        password_hash="test-password-hash",
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
            Habit(id=2, user=user, title="喝水 2000 ml", category="Body", last_check_in=fixed_now),
            Habit(id=3, user=other_user, title="夜間伸展", category="Body"),
        ]
    )
    db.commit()
