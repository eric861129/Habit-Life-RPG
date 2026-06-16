from datetime import datetime

from sqlalchemy.orm import Session

from backend.app.models import Habit, User


def test_habit_list_returns_only_current_user_habits(client, auth_headers) -> None:
    response = client.get("/api/v1/habits", headers=auth_headers)

    assert response.status_code == 200
    habits = response.json()
    assert [habit["id"] for habit in habits] == [1, 2]
    assert {habit["id"] for habit in habits} == {1, 2}
    assert 3 not in {habit["id"] for habit in habits}


def test_habit_list_returns_contract_fields_and_today_state(client, auth_headers) -> None:
    response = client.get("/api/v1/habits", headers=auth_headers)

    assert response.status_code == 200
    habits = response.json()
    assert {"id", "title", "category", "last_check_in", "checked_in_today"} == set(habits[0])
    assert habits[0]["checked_in_today"] is False
    assert habits[1]["checked_in_today"] is True


def test_checkin_success_updates_response_and_database(
    client,
    auth_headers,
    db_session: Session,
    fixed_now: datetime,
) -> None:
    response = client.post("/api/v1/habits/1/checkin", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == {
        "habit_id": 1,
        "checked_in": True,
        "current_exp": 160,
        "current_gold": 43,
        "current_level": 2,
        "leveled_up": False,
    }

    user = db_session.get(User, 1)
    habit = db_session.get(Habit, 1)
    assert user is not None
    assert habit is not None
    assert user.exp == 160
    assert user.gold == 43
    assert user.level == 2
    assert habit.last_check_in is not None
    assert habit.last_check_in.replace(tzinfo=fixed_now.tzinfo) == fixed_now


def test_checkin_duplicate_returns_400_and_does_not_update_player(
    client,
    auth_headers,
    db_session: Session,
) -> None:
    response = client.post("/api/v1/habits/2/checkin", headers=auth_headers)

    assert response.status_code == 400
    assert response.json() == {"detail": "Habit already checked in today."}
    assert_player_state(db_session)


def test_checkin_for_other_users_habit_returns_403_and_does_not_update_player(
    client,
    auth_headers,
    db_session: Session,
) -> None:
    response = client.post("/api/v1/habits/3/checkin", headers=auth_headers)

    assert response.status_code == 403
    assert response.json() == {"detail": "You do not have permission to check in this habit."}
    assert_player_state(db_session)


def test_checkin_missing_habit_returns_404_and_does_not_update_player(
    client,
    auth_headers,
    db_session: Session,
) -> None:
    response = client.post("/api/v1/habits/999/checkin", headers=auth_headers)

    assert response.status_code == 404
    assert response.json() == {"detail": "Habit not found."}
    assert_player_state(db_session)


def test_checkin_without_token_returns_401_and_does_not_update_player(
    client,
    db_session: Session,
) -> None:
    response = client.post("/api/v1/habits/1/checkin")

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated."}
    assert_player_state(db_session)


def assert_player_state(db_session: Session) -> None:
    user = db_session.get(User, 1)
    assert user is not None
    assert user.exp == 120
    assert user.gold == 35
    assert user.level == 2
