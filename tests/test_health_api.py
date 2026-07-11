from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session


def test_liveness_and_readiness_are_public(client: TestClient):
    live = client.get("/health/live")
    ready = client.get("/health/ready")

    assert live.status_code == 200
    assert live.json() == {"status": "ok"}
    assert ready.status_code == 200
    assert ready.json() == {"status": "ready"}


def test_readiness_returns_503_when_the_database_is_unavailable(
    client: TestClient,
    db_session: Session,
    monkeypatch,
):
    def fail_query(*args, **kwargs):
        del args, kwargs
        raise OperationalError("SELECT 1", {}, Exception("database offline"))

    monkeypatch.setattr(db_session, "execute", fail_query)

    response = client.get("/health/ready")

    assert response.status_code == 503
    assert response.json() == {"detail": "Database unavailable."}
