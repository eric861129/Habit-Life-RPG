from datetime import date
from pathlib import Path

import pytest
import yaml
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.database import Base
from backend.app.models import Habit, HabitCheckin, User


ROOT = Path(__file__).resolve().parents[1]


def test_model_metadata_contains_the_three_mvp_tables():
    assert set(Base.metadata.tables) == {"users", "habits", "habit_checkins"}


def test_one_habit_can_only_have_one_checkin_per_calendar_day(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'contract.db'}")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        user = User(username="Reader", username_normalized="reader", password_hash="hash")
        habit = Habit(user=user, title="Read 20 minutes")
        db.add(user)
        db.flush()
        db.add_all(
            [
                HabitCheckin(
                    user_id=user.id,
                    habit_id=habit.id,
                    checkin_date=date(2026, 7, 11),
                    exp_earned=40,
                    gold_earned=8,
                ),
                HabitCheckin(
                    user_id=user.id,
                    habit_id=habit.id,
                    checkin_date=date(2026, 7, 11),
                    exp_earned=40,
                    gold_earned=8,
                ),
            ]
        )
        with pytest.raises(IntegrityError):
            db.commit()

    engine.dispose()


def test_initial_migration_upgrades_an_empty_sqlite_database(tmp_path):
    database_path = tmp_path / "migration.db"
    config = Config(str(ROOT / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", f"sqlite:///{database_path}")

    command.upgrade(config, "head")

    tables = set(inspect(create_engine(f"sqlite:///{database_path}")).get_table_names())
    assert {"alembic_version", "users", "habits", "habit_checkins"} <= tables


def test_committed_openapi_declares_every_book_mvp_endpoint():
    contract = yaml.safe_load((ROOT / "docs" / "openapi.yaml").read_text(encoding="utf-8"))
    paths = contract["paths"]

    assert set(paths) == {
        "/api/v1/auth/register",
        "/api/v1/auth/login",
        "/api/v1/user/profile",
        "/api/v1/habits",
        "/api/v1/habits/{habit_id}",
        "/api/v1/habits/{habit_id}/checkins",
        "/health/live",
        "/health/ready",
    }
    assert "post" in paths["/api/v1/habits/{habit_id}/checkins"]
    assert "409" in paths["/api/v1/habits/{habit_id}/checkins"]["post"]["responses"]


def test_architecture_documents_name_sqlite_and_azure_sql():
    architecture = (ROOT / "docs" / "system-architecture.md").read_text(encoding="utf-8")
    database = (ROOT / "docs" / "database-schema.md").read_text(encoding="utf-8")

    assert "SQLite" in architecture
    assert "Azure SQL" in architecture
    assert "uq_habit_checkin_day" in database
    assert "Alembic" in database
