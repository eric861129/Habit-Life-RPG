from datetime import date
from pathlib import Path

import pytest
import yaml
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect
from sqlalchemy.dialects import mssql
from sqlalchemy.exc import IntegrityError
from sqlalchemy.schema import CreateTable
from sqlalchemy.orm import Session

from backend.app.database import Base
from backend.app.models import Habit, HabitCheckin, User
from backend.app.routers.habits import habit_list_statement
from backend.migrations.database_url import resolve_migration_database_url


ROOT = Path(__file__).resolve().parents[1]


def test_model_metadata_contains_the_three_mvp_tables():
    assert set(Base.metadata.tables) == {"users", "habits", "habit_checkins"}


def test_checkin_foreign_keys_avoid_sql_server_multiple_cascade_paths():
    foreign_keys = {
        foreign_key.parent.name: foreign_key.ondelete
        for foreign_key in Base.metadata.tables["habit_checkins"].foreign_keys
    }

    assert foreign_keys == {"habit_id": "CASCADE", "user_id": None}


def test_reader_text_columns_compile_to_sql_server_unicode_types():
    users_ddl = str(CreateTable(Base.metadata.tables["users"]).compile(dialect=mssql.dialect()))
    habits_ddl = str(CreateTable(Base.metadata.tables["habits"]).compile(dialect=mssql.dialect()))

    assert "username NVARCHAR(32)" in users_ddl
    assert "username_normalized NVARCHAR(32)" in users_ddl
    assert "title NVARCHAR(120)" in habits_ddl
    assert "description NVARCHAR(500)" in habits_ddl
    assert "category NVARCHAR(40)" in habits_ddl


def test_active_habit_filter_compiles_for_sql_server_bit_columns():
    statement = habit_list_statement(user_id=7, include_archived=False)
    sql = str(
        statement.compile(
            dialect=mssql.dialect(),
            compile_kwargs={"literal_binds": True},
        )
    )

    assert "habits.is_archived = 0" in sql
    assert "habits.is_archived IS 0" not in sql


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


def test_migration_prefers_database_url_from_environment(tmp_path, monkeypatch):
    database_path = tmp_path / "environment-target.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{database_path}")
    config = Config(str(ROOT / "alembic.ini"))

    command.upgrade(config, "head")

    assert database_path.exists()
    tables = set(inspect(create_engine(f"sqlite:///{database_path}")).get_table_names())
    assert "habit_checkins" in tables


def test_migration_uses_split_azure_sql_settings(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("DATABASE_HOST", "hlr-example.database.windows.net")
    monkeypatch.setenv("DATABASE_NAME", "habit-life-rpg")
    monkeypatch.setenv("DATABASE_USER", "hlradmin")
    monkeypatch.setenv("DATABASE_PASSWORD", "not-a-real-secret")

    url = resolve_migration_database_url("sqlite:///./habit_life_rpg.db")

    assert url.startswith("mssql+pyodbc:///?odbc_connect=")
    assert "hlr-example.database.windows.net" in url


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
