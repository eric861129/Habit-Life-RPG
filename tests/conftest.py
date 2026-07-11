from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from backend.app.config import Settings, get_settings
from backend.app.database import Base, create_database_engine, get_db
from backend.app.main import create_app


@pytest.fixture
def settings() -> Settings:
    return Settings(
        DATABASE_URL="sqlite:///./test-only.db",
        HLR_JWT_SECRET="test-secret-that-is-long-and-not-for-production",
        HLR_ACCESS_TOKEN_MINUTES=60,
        HLR_APP_TIMEZONE="Asia/Taipei",
        HLR_ALLOWED_ORIGINS="http://localhost:5173",
        HLR_ENVIRONMENT="test",
    )


@pytest.fixture
def db_session(tmp_path) -> Generator[Session, None, None]:
    engine = create_database_engine(f"sqlite:///{tmp_path / 'test.db'}")
    testing_session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    Base.metadata.create_all(engine)
    with testing_session() as session:
        yield session
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def client(db_session: Session, settings: Settings) -> Generator[TestClient, None, None]:
    app = create_app()

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_settings] = lambda: settings
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def register_user(client: TestClient, username: str = "reader") -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/register",
        json={"username": username, "password": "BookDemo!2026"},
    )
    assert response.status_code == 201, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def create_habit(client: TestClient, headers: dict[str, str], title: str = "Read 20 minutes") -> int:
    response = client.post(
        "/api/v1/habits",
        headers=headers,
        json={"title": title, "description": "Read before bed", "category": "Mind"},
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]
