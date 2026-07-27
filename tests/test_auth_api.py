from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models import User
from tests.conftest import register_user


def test_register_returns_token_and_authenticated_profile(client: TestClient):
    registration = client.post(
        "/api/v1/auth/register",
        json={"username": "Reader", "password": "BookDemo!2026"},
    )
    headers = {"Authorization": f"Bearer {registration.json()['access_token']}"}

    response = client.get("/api/v1/user/profile", headers=headers)

    assert registration.status_code == 201
    assert registration.json()["expires_in"] == 3600
    assert response.status_code == 200
    assert response.json() == {"id": 1, "username": "Reader", "level": 1, "exp": 0, "gold": 0}


def test_registration_hashes_password_instead_of_storing_plaintext(
    client: TestClient,
    db_session: Session,
):
    register_user(client)

    user = db_session.scalar(select(User))

    assert user is not None
    assert user.password_hash != "BookDemo!2026"
    assert user.password_hash.startswith("$argon2")


def test_casefolded_duplicate_username_returns_conflict(client: TestClient):
    register_user(client, "Reader")

    response = client.post(
        "/api/v1/auth/register",
        json={"username": "reader", "password": "AnotherPass!2026"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Username is already registered."


def test_login_accepts_casefolded_username_and_rejects_wrong_password(client: TestClient):
    register_user(client, "Reader")

    accepted = client.post(
        "/api/v1/auth/login",
        json={"username": "reader", "password": "BookDemo!2026"},
    )
    rejected = client.post(
        "/api/v1/auth/login",
        json={"username": "Reader", "password": "WrongPass!2026"},
    )

    assert accepted.status_code == 200
    assert accepted.json()["token_type"] == "bearer"
    assert rejected.status_code == 401
    assert rejected.json()["detail"] == "Invalid username or password."


def test_login_returns_token_lifetime_in_seconds(client: TestClient):
    register_user(client, "Reader")

    response = client.post(
        "/api/v1/auth/login",
        json={"username": "Reader", "password": "BookDemo!2026"},
    )

    assert response.status_code == 200
    assert response.json()["expires_in"] == 3600


def test_protected_route_rejects_missing_or_invalid_token(client: TestClient):
    missing = client.get("/api/v1/user/profile")
    invalid = client.get(
        "/api/v1/user/profile",
        headers={"Authorization": "Bearer not-a-real-token"},
    )

    assert missing.status_code == 401
    assert invalid.status_code == 401
