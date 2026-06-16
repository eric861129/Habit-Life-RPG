# Chapter 5 Backend SQLite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Chapter 5 local backend for Habit Life RPG with FastAPI, SQLite, SQLAlchemy models, development-only auth, and the three endpoints already defined in `docs/openapi.yaml`.

**Architecture:** Chapter 5 turns the Chapter 4 contract into a runnable local API without starting the React frontend or Azure deployment. The FastAPI app owns authentication guards, database access, reward calculation, and response shaping; the SQLite database is local-only and ignored by Git. Chapter 6 will expand the pytest safety net, so Chapter 5 keeps tests to smoke-level verification and contract alignment.

**Tech Stack:** Python 3.11+, FastAPI, Uvicorn, SQLAlchemy 2.x, Pydantic v2, pydantic-settings, SQLite, pytest/httpx for minimal smoke checks.

---

## Scope

Chapter 5 should produce a working backend that readers can run locally and inspect through FastAPI Swagger UI.

Included:

- FastAPI project scaffold.
- SQLite connection and SQLAlchemy ORM models.
- `Users` / `Habits` schema implementation from `docs/database-schema.md`.
- Development-only bearer token guard.
- Seed data for book screenshots and manual API calls.
- `GET /api/v1/user/profile`.
- `GET /api/v1/habits`.
- `POST /api/v1/habits/{habit_id}/checkin`.
- Chapter guide, README progress update, and book asset register update.
- Checkpoint tags and final GitHub Release.

Excluded:

- React app.
- Real JWT login flow.
- Password verification endpoint.
- Alembic migrations.
- Azure SQL / App Service / Static Web Apps.
- Full pytest matrix, coverage gates, or CI. Those belong to Chapter 6.
- Full check-in history table. MVP still uses `Habits.last_check_in`.

## Version Tags

Use these checkpoint tags:

| Step | Tag | Meaning |
| :--- | :--- | :--- |
| 5.1 | `ch05-1-fastapi-skeleton` | Python package and FastAPI app can start |
| 5.2 | `ch05-2-sqlite-models` | SQLite connection, ORM models, seed data |
| 5.3 | `ch05-3-profile-habits-api` | profile and habit list endpoints work |
| 5.4 | `ch05-4-checkin-api` | check-in endpoint and RPG reward loop work |
| Wrap-up | `ch05-backend-sqlite` | Chapter 5 complete and released |

## File Structure

Create or modify these files:

```text
pyproject.toml
.env.example
README.md
backend/
  __init__.py
  app/
    __init__.py
    config.py
    database.py
    main.py
    models.py
    schemas.py
    security.py
    seed.py
    services/
      __init__.py
      rewards.py
    routers/
      __init__.py
      user.py
      habits.py
tests/
  __init__.py
  test_ch05_smoke.py
docs/
  chapter-guides/
    ch05-backend-sqlite.md
  book-assets/
    assets-register.md
    ch05-backend/
      README.md
```

Responsibilities:

- `backend/app/main.py`: FastAPI app creation, startup lifespan, router registration.
- `backend/app/config.py`: environment-backed settings.
- `backend/app/database.py`: SQLAlchemy engine, session dependency, SQLite foreign key behavior.
- `backend/app/models.py`: `User` and `Habit` ORM models.
- `backend/app/schemas.py`: Pydantic response models matching `docs/openapi.yaml`.
- `backend/app/security.py`: development bearer token guard and current-user dependency.
- `backend/app/seed.py`: deterministic demo data for book screenshots.
- `backend/app/services/rewards.py`: reward and level-up rules.
- `backend/app/routers/user.py`: `GET /api/v1/user/profile`.
- `backend/app/routers/habits.py`: `GET /api/v1/habits` and `POST /api/v1/habits/{habit_id}/checkin`.
- `tests/test_ch05_smoke.py`: minimal smoke checks only; Chapter 6 will broaden coverage.

## API And Data Contract

Keep the Chapter 4 contract unchanged:

- `GET /api/v1/user/profile`
- `GET /api/v1/habits`
- `POST /api/v1/habits/{habit_id}/checkin`

Check-in success response must contain:

```json
{
  "habit_id": 1,
  "checked_in": true,
  "current_exp": 160,
  "current_gold": 43,
  "current_level": 2,
  "leveled_up": false
}
```

Error response must remain:

```json
{
  "detail": "..."
}
```

Do not introduce `task_id`, `TaskId`, `taskId`, `new_gold`, `new_exp`, or `level_up`.

## Reward Rule For Chapter 5

Use the fixed MVP rule implied by Chapter 3 UI examples:

- Successful check-in grants `+40 EXP`.
- Successful check-in grants `+8 gold`.
- A user levels up when the updated EXP reaches `current_level * 200`.
- EXP remains cumulative in Chapter 5. Do not reset EXP to zero on level-up.
- HP is stored and returned from profile, but HP penalties are not implemented in Chapter 5.

Example:

```python
CHECKIN_EXP_REWARD = 40
CHECKIN_GOLD_REWARD = 8

def apply_checkin_reward(user: User) -> bool:
    user.exp += CHECKIN_EXP_REWARD
    user.gold += CHECKIN_GOLD_REWARD

    threshold = user.level * 200
    leveled_up = user.exp >= threshold
    if leveled_up:
        user.level += 1

    return leveled_up
```

## Task 1: FastAPI Skeleton

**Files:**

- Create: `pyproject.toml`
- Create: `backend/__init__.py`
- Create: `backend/app/__init__.py`
- Create: `backend/app/main.py`
- Modify: `.env.example`

- [ ] **Step 1: Confirm clean starting point**

Run:

```bash
git status --short --branch
```

Expected:

```text
## main...origin/main
```

- [ ] **Step 2: Create Python project metadata**

Create `pyproject.toml`:

```toml
[project]
name = "habit-life-rpg"
version = "0.5.0"
description = "Chapter 5 local FastAPI backend for Habit Life RPG."
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115.0",
    "pydantic-settings>=2.6.0",
    "sqlalchemy>=2.0.36",
    "uvicorn[standard]>=0.32.0"
]

[project.optional-dependencies]
dev = [
    "httpx>=0.27.2",
    "pytest>=8.3.0"
]

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.ruff]
line-length = 100
target-version = "py311"
```

- [ ] **Step 3: Update local environment example**

Update `.env.example` so Chapter 5 uses the same local SQLite URL as the backend:

```dotenv
# Local development database.
# Chapter 5 starts with SQLite before Chapter 8 moves to Azure SQL.
DATABASE_URL=sqlite:///./habit_life_rpg.db

# Development-only bearer token for Chapter 5.
# This is not a production JWT. Replace locally in .env if needed.
HLR_DEV_AUTH_TOKEN=local-dev-token

# Development-only JWT secret placeholder for future auth chapters.
# Replace locally in .env. Never commit the real value.
JWT_SECRET_KEY=replace-with-local-development-secret

# Frontend API root.
# Chapter 7 uses localhost; Chapter 8 switches this to Azure App Service.
VITE_API_BASE_URL=http://localhost:8000

# Optional frontend telemetry setting for Chapter 7.5 / Chapter 8.
# This value is configuration, but do not send personal data through telemetry.
VITE_APPINSIGHTS_CONNECTION_STRING=
```

- [ ] **Step 4: Add package markers**

Create empty package marker files:

```python
# backend/__init__.py
```

```python
# backend/app/__init__.py
```

- [ ] **Step 5: Create minimal FastAPI app**

Create `backend/app/main.py`:

```python
from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI(
        title="Habit Life RPG API",
        version="0.5.0",
        description="Chapter 5 local FastAPI backend for Habit Life RPG.",
    )
    return app


app = create_app()
```

- [ ] **Step 6: Install dependencies locally**

Run:

```bash
python -m pip install -e ".[dev]"
```

Expected:

```text
Successfully installed habit-life-rpg
```

- [ ] **Step 7: Verify Python imports**

Run:

```bash
python -m compileall backend
```

Expected:

```text
Listing 'backend'...
```

- [ ] **Step 8: Commit and tag checkpoint**

Run:

```bash
git add pyproject.toml .env.example backend
git commit -m "feat: add chapter 5 FastAPI skeleton"
git tag -a ch05-1-fastapi-skeleton -m "Chapter 5.1 FastAPI skeleton"
```

## Task 2: SQLite Models And Seed Data

**Files:**

- Create: `backend/app/config.py`
- Create: `backend/app/database.py`
- Create: `backend/app/models.py`
- Create: `backend/app/seed.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: Add settings**

Create `backend/app/config.py`:

```python
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Field("sqlite:///./habit_life_rpg.db", validation_alias="DATABASE_URL")
    dev_auth_token: str = Field("local-dev-token", validation_alias="HLR_DEV_AUTH_TOKEN")
    demo_user_id: int = Field(1, validation_alias="HLR_DEMO_USER_ID")
    app_timezone: str = Field("Asia/Taipei", validation_alias="HLR_APP_TIMEZONE")

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

- [ ] **Step 2: Add database engine and session dependency**

Create `backend/app/database.py`:

```python
from collections.abc import Generator

from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy import create_engine

from backend.app.config import get_settings


class Base(DeclarativeBase):
    pass


settings = get_settings()

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


@event.listens_for(Engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, connection_record) -> None:
    if settings.database_url.startswith("sqlite"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from backend.app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
```

- [ ] **Step 3: Add ORM models**

Create `backend/app/models.py`:

```python
from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database import Base


TAIPEI = ZoneInfo("Asia/Taipei")


def now_taipei() -> datetime:
    return datetime.now(TAIPEI)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    exp: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    gold: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    hp: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=now_taipei,
    )

    habits: Mapped[list["Habit"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Habit(Base):
    __tablename__ = "habits"
    __table_args__ = (
        Index("ix_habits_user_id_last_check_in", "user_id", "last_check_in"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    category: Mapped[str | None] = mapped_column(String(60), nullable=True)
    last_check_in: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=now_taipei,
    )

    user: Mapped[User] = relationship(back_populates="habits")
```

- [ ] **Step 4: Add deterministic seed data**

Create `backend/app/seed.py`:

```python
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
```

- [ ] **Step 5: Initialize database during app startup**

Modify `backend/app/main.py`:

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.app.database import SessionLocal, init_db
from backend.app.seed import seed_demo_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    with SessionLocal() as db:
        seed_demo_data(db)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Habit Life RPG API",
        version="0.5.0",
        description="Chapter 5 local FastAPI backend for Habit Life RPG.",
        lifespan=lifespan,
    )
    return app


app = create_app()
```

- [ ] **Step 6: Verify database startup**

Run:

```bash
python -m compileall backend
python -m uvicorn backend.app.main:app --port 8000
```

Expected:

```text
Application startup complete.
Uvicorn running on http://127.0.0.1:8000
```

Stop the server with `Ctrl+C`.

- [ ] **Step 7: Confirm SQLite file is ignored**

Run:

```bash
git status --short
```

Expected: `habit_life_rpg.db` must not appear because `.gitignore` already excludes `*.db`.

- [ ] **Step 8: Commit and tag checkpoint**

Run:

```bash
git add backend/app/config.py backend/app/database.py backend/app/models.py backend/app/seed.py backend/app/main.py
git commit -m "feat: add chapter 5 SQLite models"
git tag -a ch05-2-sqlite-models -m "Chapter 5.2 SQLite models"
```

## Task 3: Schemas And Development Auth Guard

**Files:**

- Create: `backend/app/schemas.py`
- Create: `backend/app/security.py`

- [ ] **Step 1: Add Pydantic response schemas**

Create `backend/app/schemas.py`:

```python
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
```

- [ ] **Step 2: Add development-only auth dependency**

Create `backend/app/security.py`:

```python
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.app.config import Settings, get_settings
from backend.app.database import get_db
from backend.app.models import User


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> User:
    if credentials is None or credentials.credentials != settings.dev_auth_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated.",
        )

    user = db.get(User, settings.demo_user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated.",
        )
    return user
```

- [ ] **Step 3: Verify import health**

Run:

```bash
python -m compileall backend
```

Expected:

```text
Listing 'backend/app'...
```

- [ ] **Step 4: Commit**

Run:

```bash
git add backend/app/schemas.py backend/app/security.py
git commit -m "feat: add chapter 5 schemas and auth guard"
```

Do not tag yet; tag `ch05-3-profile-habits-api` after the profile and habit list endpoints are implemented.

## Task 4: Profile And Habit List API

**Files:**

- Create: `backend/app/routers/__init__.py`
- Create: `backend/app/routers/user.py`
- Create: `backend/app/routers/habits.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: Add router package marker**

Create `backend/app/routers/__init__.py`:

```python
# Router package for Chapter 5 API endpoints.
```

- [ ] **Step 2: Add profile endpoint**

Create `backend/app/routers/user.py`:

```python
from typing import Annotated

from fastapi import APIRouter, Depends

from backend.app.models import User
from backend.app.schemas import UserProfile
from backend.app.security import get_current_user


router = APIRouter(prefix="/api/v1/user", tags=["User"])


@router.get("/profile", response_model=UserProfile)
def get_profile(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    return current_user
```

- [ ] **Step 3: Add habit list helper and endpoint**

Create `backend/app/routers/habits.py`:

```python
from datetime import datetime
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.config import Settings, get_settings
from backend.app.database import get_db
from backend.app.models import Habit, User
from backend.app.schemas import HabitRead
from backend.app.security import get_current_user


router = APIRouter(prefix="/api/v1/habits", tags=["Habits"])


def is_checked_in_today(last_check_in: datetime | None, settings: Settings) -> bool:
    if last_check_in is None:
        return False

    timezone = ZoneInfo(settings.app_timezone)
    if last_check_in.tzinfo is None:
        last_check_in = last_check_in.replace(tzinfo=timezone)

    today = datetime.now(timezone).date()
    return last_check_in.astimezone(timezone).date() == today


def to_habit_read(habit: Habit, settings: Settings) -> HabitRead:
    return HabitRead(
        id=habit.id,
        title=habit.title,
        category=habit.category,
        last_check_in=habit.last_check_in,
        checked_in_today=is_checked_in_today(habit.last_check_in, settings),
    )


@router.get("", response_model=list[HabitRead])
def list_habits(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> list[HabitRead]:
    habits = db.scalars(
        select(Habit)
        .where(Habit.user_id == current_user.id)
        .order_by(Habit.id)
    ).all()
    return [to_habit_read(habit, settings) for habit in habits]
```

- [ ] **Step 4: Register routers**

Modify `backend/app/main.py`:

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.app.database import SessionLocal, init_db
from backend.app.routers import habits, user
from backend.app.seed import seed_demo_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    with SessionLocal() as db:
        seed_demo_data(db)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Habit Life RPG API",
        version="0.5.0",
        description="Chapter 5 local FastAPI backend for Habit Life RPG.",
        lifespan=lifespan,
    )
    app.include_router(user.router)
    app.include_router(habits.router)
    return app


app = create_app()
```

- [ ] **Step 5: Verify endpoints manually**

Run server:

```bash
python -m uvicorn backend.app.main:app --port 8000
```

In another terminal, run:

```bash
curl -s http://127.0.0.1:8000/api/v1/user/profile \
  -H "Authorization: Bearer local-dev-token"
```

Expected profile shape:

```json
{"id":1,"username":"arthur","level":2,"exp":120,"gold":35,"hp":86}
```

Run:

```bash
curl -s http://127.0.0.1:8000/api/v1/habits \
  -H "Authorization: Bearer local-dev-token"
```

Expected: JSON array containing habit `id` values `1` and `2`, with `checked_in_today`.

- [ ] **Step 6: Verify unauthorized response**

Run:

```bash
curl -s -i http://127.0.0.1:8000/api/v1/user/profile
```

Expected:

```text
HTTP/1.1 401 Unauthorized
```

Body:

```json
{"detail":"Not authenticated."}
```

- [ ] **Step 7: Commit and tag checkpoint**

Run:

```bash
git add backend/app/main.py backend/app/routers
git commit -m "feat: add chapter 5 profile and habit APIs"
git tag -a ch05-3-profile-habits-api -m "Chapter 5.3 profile and habit APIs"
```

## Task 5: Check-In API And Reward Service

**Files:**

- Create: `backend/app/services/__init__.py`
- Create: `backend/app/services/rewards.py`
- Modify: `backend/app/routers/habits.py`

- [ ] **Step 1: Add service package marker**

Create `backend/app/services/__init__.py`:

```python
# Service package for Chapter 5 backend rules.
```

- [ ] **Step 2: Add reward service**

Create `backend/app/services/rewards.py`:

```python
from backend.app.models import User


CHECKIN_EXP_REWARD = 40
CHECKIN_GOLD_REWARD = 8


def apply_checkin_reward(user: User) -> bool:
    user.exp += CHECKIN_EXP_REWARD
    user.gold += CHECKIN_GOLD_REWARD

    threshold = user.level * 200
    leveled_up = user.exp >= threshold
    if leveled_up:
        user.level += 1

    return leveled_up
```

- [ ] **Step 3: Add check-in endpoint**

Modify `backend/app/routers/habits.py` to include the `POST /{habit_id}/checkin` route:

```python
from datetime import datetime
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.config import Settings, get_settings
from backend.app.database import get_db
from backend.app.models import Habit, User
from backend.app.schemas import HabitCheckinResponse, HabitRead
from backend.app.security import get_current_user
from backend.app.services.rewards import apply_checkin_reward


router = APIRouter(prefix="/api/v1/habits", tags=["Habits"])


def current_time(settings: Settings) -> datetime:
    return datetime.now(ZoneInfo(settings.app_timezone))


def is_checked_in_today(last_check_in: datetime | None, settings: Settings) -> bool:
    if last_check_in is None:
        return False

    timezone = ZoneInfo(settings.app_timezone)
    if last_check_in.tzinfo is None:
        last_check_in = last_check_in.replace(tzinfo=timezone)

    today = current_time(settings).date()
    return last_check_in.astimezone(timezone).date() == today


def to_habit_read(habit: Habit, settings: Settings) -> HabitRead:
    return HabitRead(
        id=habit.id,
        title=habit.title,
        category=habit.category,
        last_check_in=habit.last_check_in,
        checked_in_today=is_checked_in_today(habit.last_check_in, settings),
    )


@router.get("", response_model=list[HabitRead])
def list_habits(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> list[HabitRead]:
    habits = db.scalars(
        select(Habit)
        .where(Habit.user_id == current_user.id)
        .order_by(Habit.id)
    ).all()
    return [to_habit_read(habit, settings) for habit in habits]


@router.post("/{habit_id}/checkin", response_model=HabitCheckinResponse)
def check_in_habit(
    habit_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> HabitCheckinResponse:
    habit = db.get(Habit, habit_id)
    if habit is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found.",
        )

    if habit.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to check in this habit.",
        )

    if is_checked_in_today(habit.last_check_in, settings):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Habit already checked in today.",
        )

    habit.last_check_in = current_time(settings)
    leveled_up = apply_checkin_reward(current_user)
    db.commit()
    db.refresh(current_user)
    db.refresh(habit)

    return HabitCheckinResponse(
        habit_id=habit.id,
        checked_in=True,
        current_exp=current_user.exp,
        current_gold=current_user.gold,
        current_level=current_user.level,
        leveled_up=leveled_up,
    )
```

- [ ] **Step 4: Verify success check-in**

Start server:

```bash
python -m uvicorn backend.app.main:app --port 8000
```

Run:

```bash
curl -s -X POST http://127.0.0.1:8000/api/v1/habits/1/checkin \
  -H "Authorization: Bearer local-dev-token"
```

Expected:

```json
{"habit_id":1,"checked_in":true,"current_exp":160,"current_gold":43,"current_level":2,"leveled_up":false}
```

- [ ] **Step 5: Verify duplicate check-in**

Run the same check-in command again.

Expected:

```json
{"detail":"Habit already checked in today."}
```

HTTP status must be `400`.

- [ ] **Step 6: Verify forbidden check-in**

Run:

```bash
curl -s -i -X POST http://127.0.0.1:8000/api/v1/habits/3/checkin \
  -H "Authorization: Bearer local-dev-token"
```

Expected:

```text
HTTP/1.1 403 Forbidden
```

Body:

```json
{"detail":"You do not have permission to check in this habit."}
```

- [ ] **Step 7: Verify not-found check-in**

Run:

```bash
curl -s -i -X POST http://127.0.0.1:8000/api/v1/habits/999/checkin \
  -H "Authorization: Bearer local-dev-token"
```

Expected:

```text
HTTP/1.1 404 Not Found
```

Body:

```json
{"detail":"Habit not found."}
```

- [ ] **Step 8: Commit and tag checkpoint**

Run:

```bash
git add backend/app/routers/habits.py backend/app/services
git commit -m "feat: add chapter 5 habit check-in API"
git tag -a ch05-4-checkin-api -m "Chapter 5.4 habit check-in API"
```

## Task 6: Minimal Smoke Tests

**Files:**

- Create: `tests/__init__.py`
- Create: `tests/test_ch05_smoke.py`

- [ ] **Step 1: Add test package marker**

Create `tests/__init__.py`:

```python
# Test package for Habit Life RPG.
```

- [ ] **Step 2: Add smoke tests**

Create `tests/test_ch05_smoke.py`:

```python
from fastapi.testclient import TestClient

from backend.app.main import app


AUTH_HEADERS = {"Authorization": "Bearer local-dev-token"}


def test_profile_requires_auth() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/user/profile")

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated."}


def test_profile_returns_demo_user() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/user/profile", headers=AUTH_HEADERS)

    assert response.status_code == 200
    assert response.json()["username"] == "arthur"
    assert {"id", "username", "level", "exp", "gold", "hp"} <= set(response.json())


def test_habit_list_uses_habit_contract() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/habits", headers=AUTH_HEADERS)

    assert response.status_code == 200
    first_habit = response.json()[0]
    assert {"id", "title", "category", "last_check_in", "checked_in_today"} <= set(first_habit)
```

These tests intentionally avoid the full error matrix. Chapter 6 will add isolated test database fixtures and the check-in edge cases.

- [ ] **Step 3: Run smoke tests**

Run:

```bash
python -m pytest tests/test_ch05_smoke.py -q
```

Expected:

```text
3 passed
```

- [ ] **Step 4: Commit**

Run:

```bash
git add tests
git commit -m "test: add chapter 5 backend smoke checks"
```

Do not create a checkpoint tag here unless the book manuscript explicitly needs a separate testing screenshot.

## Task 7: Chapter Documentation And Asset Tracking

**Files:**

- Create: `docs/chapter-guides/ch05-backend-sqlite.md`
- Create: `docs/book-assets/ch05-backend/README.md`
- Modify: `docs/book-assets/assets-register.md`
- Modify: `README.md`

- [ ] **Step 1: Add Chapter 5 guide**

Create `docs/chapter-guides/ch05-backend-sqlite.md` with these sections:

```markdown
# 第 5 章導覽：後端開發

對應書稿：第 5 章「後端開發」  
Git tag：`ch05-backend-sqlite`  
本章定位：依照第 4 章契約建立本機 FastAPI + SQLite 後端。

## 本章你會看到什麼

- FastAPI app scaffold。
- SQLite database connection。
- SQLAlchemy `User` / `Habit` models。
- 開發用 bearer token guard。
- `GET /api/v1/user/profile`。
- `GET /api/v1/habits`。
- `POST /api/v1/habits/{habit_id}/checkin`。

## 啟動方式

```bash
python -m pip install -e ".[dev]"
python -m uvicorn backend.app.main:app --reload --port 8000
```

## 開發用 API Token

本章使用 development-only token：

```http
Authorization: Bearer local-dev-token
```

這不是正式 JWT，也不是 production auth。正式登入與資安強化會在後續章節擴充。

## 第五章邊界

- 不建立 React app。
- 不建立 Azure 資源。
- 不建立 Alembic migration。
- 不建立完整登入註冊流程。
- 不建立完整 Pytest 測試矩陣。
```

- [ ] **Step 2: Add Chapter 5 asset README**

Create `docs/book-assets/ch05-backend/README.md`:

```markdown
# Chapter 5 Backend Assets

本資料夾追蹤第 5 章「後端開發」可放入書稿的圖片素材。

| 圖號 | 來源 | 狀態 | 說明 |
| :--- | :--- | :--- | :--- |
| 圖 5-1-1 | terminal / project tree | planned | FastAPI backend 專案結構 |
| 圖 5-1-2 | browser `/docs` | planned | FastAPI Swagger UI |
| 圖 5-2-1 | `backend/app/models.py` | planned | `User` / `Habit` ORM model |
| 圖 5-3-1 | curl / API client | planned | profile 與 habit list response |
| 圖 5-4-1 | curl / API client | planned | check-in success response |
| 圖 5-4-2 | curl / API client | planned | duplicate / forbidden / not found errors |
```

- [ ] **Step 3: Update asset register**

Append rows to `docs/book-assets/assets-register.md`:

```markdown
| 圖 5-1-1 | FastAPI backend 專案結構 | terminal screenshot | `backend/` | planned | 顯示第五章開始建立後端骨架 |
| 圖 5-1-2 | FastAPI Swagger UI | browser screenshot | `http://127.0.0.1:8000/docs` | planned | 展示本機 API 文件 |
| 圖 5-2-1 | SQLAlchemy Users / Habits models | code screenshot | `backend/app/models.py` | planned | 對照第四章資料庫綱要 |
| 圖 5-3-1 | Profile and habits API response | terminal/API client screenshot | local FastAPI | planned | 展示 `GET /api/v1/user/profile` 與 `GET /api/v1/habits` |
| 圖 5-4-1 | Habit check-in success response | terminal/API client screenshot | local FastAPI | planned | 展示 `current_exp`、`current_gold`、`current_level`、`leveled_up` |
| 圖 5-4-2 | Habit check-in error responses | terminal/API client screenshot | local FastAPI | planned | 展示 400、403、404 的 `{ "detail": "..." }` |
```

- [ ] **Step 4: Update README progress**

In `README.md`:

- Change Chapter 5 status from `尚未開始` to `已完成`.
- Add a new `## 第 5 章後端開發` section above Chapter 4.
- Include checkout commands for all Chapter 5 tags.
- State that Chapter 5 still does not include React, Azure, or full pytest coverage.

- [ ] **Step 5: Commit documentation**

Run:

```bash
git add README.md docs/chapter-guides/ch05-backend-sqlite.md docs/book-assets/assets-register.md docs/book-assets/ch05-backend/README.md
git commit -m "docs: complete chapter 5 backend guide"
```

## Task 8: Final Verification, Tag, Push, Release

**Files:**

- Verify all changed files.
- No new file creation unless validation requires a targeted fix.

- [ ] **Step 1: Run formatting and whitespace check**

Run:

```bash
git diff --check
```

Expected: no output.

- [ ] **Step 2: Run Python compile check**

Run:

```bash
python -m compileall backend tests
```

Expected: no syntax errors.

- [ ] **Step 3: Run smoke tests**

Run:

```bash
python -m pytest -q
```

Expected:

```text
3 passed
```

- [ ] **Step 4: Lint OpenAPI contract**

Run:

```bash
npx --yes @redocly/cli@latest lint docs/openapi.yaml
```

Expected:

```text
Woohoo! Your API description is valid.
```

- [ ] **Step 5: Scan for naming drift**

Run:

```bash
rg -n "task_id|TaskId|taskId|new_gold|new_exp|level_up" README.md docs backend tests prototype
```

Expected: no matches.

- [ ] **Step 6: Scan for committed secrets**

Run:

```bash
rg -n --hidden -g '!docs/book-assets/**/*.png' -g '!*.png' -g '!node_modules' -g '!dist' -g '!build' -g '!.git' '(sk-[A-Za-z0-9_-]+|AKIA[0-9A-Z]{16}|BEGIN (RSA|OPENSSH|EC|DSA) PRIVATE KEY|DefaultEndpointsProtocol=|AccountKey=|password\s*=\s*[^\s#]+|secret\s*=\s*[^\s#]+)' .
```

Expected: no matches. If `.env.example` wording causes a false positive, inspect and document the false positive before proceeding.

- [ ] **Step 7: Create final Chapter 5 tag**

Run:

```bash
git status --short --branch
git tag -a ch05-backend-sqlite -m "Chapter 5 backend SQLite"
```

Expected: worktree clean and final tag points to the documentation wrap-up commit.

- [ ] **Step 8: Push main and tags**

Run:

```bash
git push origin main
git push origin ch05-1-fastapi-skeleton ch05-2-sqlite-models ch05-3-profile-habits-api ch05-4-checkin-api ch05-backend-sqlite
```

- [ ] **Step 9: Create GitHub Release**

Run:

```bash
gh release create ch05-backend-sqlite \
  --title "Chapter 5: Backend SQLite" \
  --notes "Chapter 5 builds the local FastAPI + SQLite backend for Habit Life RPG. It implements the Chapter 4 OpenAPI contract, creates Users and Habits models, adds development-only bearer auth, seeds local demo data, and completes the habit check-in RPG reward loop."
```

- [ ] **Step 10: Verify release**

Run:

```bash
gh release view ch05-backend-sqlite --json tagName,name,url,isDraft,isPrerelease,publishedAt
```

Expected:

```json
{"isDraft":false,"isPrerelease":false,"tagName":"ch05-backend-sqlite"}
```

## Self-Review Checklist

- [ ] Every endpoint implemented in Chapter 5 exists in `docs/openapi.yaml`.
- [ ] Check-in response uses `current_exp`, `current_gold`, `current_level`, `leveled_up`.
- [ ] `User` model stores `password_hash`, never plaintext password.
- [ ] SQLite `.db` file is ignored and not committed.
- [ ] `Habits.last_check_in` powers same-day duplicate prevention.
- [ ] `403` is returned when a habit exists but belongs to another user.
- [ ] `404` is returned when a habit does not exist.
- [ ] Development token is clearly documented as local-only.
- [ ] Chapter 6 work is not pulled forward beyond smoke tests.
- [ ] README and chapter guide show reader checkout commands.
