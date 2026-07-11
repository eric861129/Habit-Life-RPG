from fastapi.testclient import TestClient

from tests.conftest import create_habit, register_user


def test_member_can_create_list_read_update_and_archive_a_habit(client: TestClient):
    headers = register_user(client)
    habit_id = create_habit(client, headers)

    listed = client.get("/api/v1/habits", headers=headers)
    read = client.get(f"/api/v1/habits/{habit_id}", headers=headers)
    updated = client.patch(
        f"/api/v1/habits/{habit_id}",
        headers=headers,
        json={"title": "Read 30 minutes", "category": "Learning"},
    )
    archived = client.delete(f"/api/v1/habits/{habit_id}", headers=headers)
    active_after_archive = client.get("/api/v1/habits", headers=headers)
    all_after_archive = client.get("/api/v1/habits?include_archived=true", headers=headers)

    assert listed.status_code == 200
    assert [habit["id"] for habit in listed.json()] == [habit_id]
    assert read.json()["title"] == "Read 20 minutes"
    assert updated.status_code == 200
    assert updated.json()["title"] == "Read 30 minutes"
    assert updated.json()["category"] == "Learning"
    assert archived.status_code == 204
    assert active_after_archive.json() == []
    assert all_after_archive.json()[0]["is_archived"] is True


def test_habit_names_are_trimmed_and_blank_names_are_rejected(client: TestClient):
    headers = register_user(client)

    created = client.post("/api/v1/habits", headers=headers, json={"title": "  Stretch  "})
    rejected = client.post("/api/v1/habits", headers=headers, json={"title": "   "})

    assert created.status_code == 201
    assert created.json()["title"] == "Stretch"
    assert rejected.status_code == 422


def test_member_cannot_discover_or_modify_another_members_habit(client: TestClient):
    first_headers = register_user(client, "first-reader")
    habit_id = create_habit(client, first_headers)
    second_headers = register_user(client, "second-reader")

    read = client.get(f"/api/v1/habits/{habit_id}", headers=second_headers)
    update = client.patch(
        f"/api/v1/habits/{habit_id}",
        headers=second_headers,
        json={"title": "Stolen"},
    )
    archive = client.delete(f"/api/v1/habits/{habit_id}", headers=second_headers)

    assert read.status_code == 404
    assert update.status_code == 404
    assert archive.status_code == 404


def test_unauthenticated_habit_requests_are_rejected(client: TestClient):
    assert client.get("/api/v1/habits").status_code == 401
    assert client.post("/api/v1/habits", json={"title": "Read"}).status_code == 401
