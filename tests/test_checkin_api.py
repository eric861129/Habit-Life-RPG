from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.models import Habit, HabitCheckin, User
from backend.app.services import checkins as checkin_service
from tests.conftest import create_habit, register_user


def set_today(monkeypatch, value: date) -> None:
    monkeypatch.setattr(checkin_service, "today_in_timezone", lambda settings: value)


def test_successful_checkin_creates_ledger_and_applies_rewards(
    client: TestClient,
    db_session: Session,
    monkeypatch,
):
    set_today(monkeypatch, date(2026, 7, 11))
    headers = register_user(client)
    habit_id = create_habit(client, headers)

    response = client.post(f"/api/v1/habits/{habit_id}/checkins", headers=headers)

    assert response.status_code == 201
    assert {
        "habit_id": habit_id,
        "checkin_date": "2026-07-11",
        "exp_earned": 40,
        "gold_earned": 8,
        "streak_count": 1,
        "current_exp": 40,
        "current_gold": 8,
        "current_level": 1,
        "leveled_up": False,
    }.items() <= response.json().items()
    assert db_session.scalar(select(func.count()).select_from(HabitCheckin)) == 1


def test_duplicate_checkin_returns_conflict_without_second_reward(
    client: TestClient,
    db_session: Session,
    monkeypatch,
):
    set_today(monkeypatch, date(2026, 7, 11))
    headers = register_user(client)
    habit_id = create_habit(client, headers)
    assert client.post(f"/api/v1/habits/{habit_id}/checkins", headers=headers).status_code == 201

    duplicate = client.post(f"/api/v1/habits/{habit_id}/checkins", headers=headers)
    user = db_session.scalar(select(User))

    assert duplicate.status_code == 409
    assert duplicate.json()["detail"] == "Habit already checked in today."
    assert db_session.scalar(select(func.count()).select_from(HabitCheckin)) == 1
    assert user is not None and (user.exp, user.gold) == (40, 8)


def test_consecutive_days_increment_streak_and_missed_days_reset_it(client: TestClient, monkeypatch):
    headers = register_user(client)
    habit_id = create_habit(client, headers)

    set_today(monkeypatch, date(2026, 7, 10))
    first = client.post(f"/api/v1/habits/{habit_id}/checkins", headers=headers)
    set_today(monkeypatch, date(2026, 7, 11))
    second = client.post(f"/api/v1/habits/{habit_id}/checkins", headers=headers)
    set_today(monkeypatch, date(2026, 7, 13))
    reset = client.post(f"/api/v1/habits/{habit_id}/checkins", headers=headers)

    assert first.json()["streak_count"] == 1
    assert second.json()["streak_count"] == 2
    assert reset.json()["streak_count"] == 1


def test_checkin_can_level_up_the_member(client: TestClient, db_session: Session, monkeypatch):
    set_today(monkeypatch, date(2026, 7, 11))
    headers = register_user(client)
    habit_id = create_habit(client, headers)
    user = db_session.scalar(select(User))
    assert user is not None
    user.exp = 190
    db_session.commit()

    response = client.post(f"/api/v1/habits/{habit_id}/checkins", headers=headers)

    assert response.status_code == 201
    assert response.json()["current_exp"] == 230
    assert response.json()["current_level"] == 2
    assert response.json()["leveled_up"] is True


def test_archived_or_other_members_habit_cannot_be_checked_in(client: TestClient, monkeypatch):
    set_today(monkeypatch, date(2026, 7, 11))
    first_headers = register_user(client, "first-reader")
    habit_id = create_habit(client, first_headers)
    second_headers = register_user(client, "second-reader")

    hidden = client.post(f"/api/v1/habits/{habit_id}/checkins", headers=second_headers)
    client.delete(f"/api/v1/habits/{habit_id}", headers=first_headers)
    archived = client.post(f"/api/v1/habits/{habit_id}/checkins", headers=first_headers)

    assert hidden.status_code == 404
    assert archived.status_code == 404


def test_habit_read_model_reflects_today_after_checkin(client: TestClient, db_session: Session, monkeypatch):
    set_today(monkeypatch, date(2026, 7, 11))
    headers = register_user(client)
    habit_id = create_habit(client, headers)
    client.post(f"/api/v1/habits/{habit_id}/checkins", headers=headers)

    habit = db_session.get(Habit, habit_id)
    response = client.get(f"/api/v1/habits/{habit_id}", headers=headers)

    assert habit is not None and habit.last_checkin_date == date(2026, 7, 11)
    assert response.json()["checked_in_today"] is True
