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
