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
