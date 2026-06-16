def test_profile_requires_auth(client) -> None:
    response = client.get("/api/v1/user/profile")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated."}


def test_profile_returns_demo_user(client, auth_headers) -> None:
    response = client.get("/api/v1/user/profile", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["username"] == "arthur"
    assert {"id", "username", "level", "exp", "gold", "hp"} <= set(response.json())


def test_habit_list_uses_habit_contract(client, auth_headers) -> None:
    response = client.get("/api/v1/habits", headers=auth_headers)
    assert response.status_code == 200
    first_habit = response.json()[0]
    assert {"id", "title", "category", "last_check_in", "checked_in_today"} <= set(first_habit)
