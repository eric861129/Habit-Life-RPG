def test_vite_localhost_origin_is_allowed(client, auth_headers) -> None:
    response = client.options(
        "/api/v1/user/profile",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization",
            **auth_headers,
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_vite_127_origin_is_allowed(client, auth_headers) -> None:
    response = client.options(
        "/api/v1/user/profile",
        headers={
            "Origin": "http://127.0.0.1:5173",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization",
            **auth_headers,
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:5173"


def test_configured_swa_origin_is_allowed(monkeypatch) -> None:
    from fastapi.testclient import TestClient

    from backend.app.config import get_settings
    from backend.app.main import create_app

    monkeypatch.setenv(
        "HLR_ALLOWED_ORIGINS",
        "http://localhost:5173,https://icy-mud-0a1b2c.azurestaticapps.net",
    )
    get_settings.cache_clear()
    app = create_app(enable_startup_seed=False)

    with TestClient(app) as test_client:
        response = test_client.options(
            "/api/v1/user/profile",
            headers={
                "Origin": "https://icy-mud-0a1b2c.azurestaticapps.net",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "authorization",
            },
        )

    get_settings.cache_clear()
    assert response.status_code == 200
    assert (
        response.headers["access-control-allow-origin"]
        == "https://icy-mud-0a1b2c.azurestaticapps.net"
    )
