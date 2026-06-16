def test_profile_without_token_returns_401(client) -> None:
    response = client.get("/api/v1/user/profile")

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated."}


def test_profile_with_token_returns_user_contract(client, auth_headers) -> None:
    response = client.get("/api/v1/user/profile", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "username": "arthur",
        "level": 2,
        "exp": 120,
        "gold": 35,
        "hp": 86,
    }
