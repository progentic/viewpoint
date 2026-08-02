import re

from fastapi.testclient import TestClient

from researcher_companion.api.app import create_app

BOUNDARY_HEADERS = {
    "Origin": "https://word-researcher.localhost:4179",
    "Sec-Fetch-Site": "same-origin",
}
INSTALLATION_SECRET = b"test-installation-secret-with-at-least-32-bytes"


def test_health_succeeds_through_valid_local_session(companion_settings) -> None:
    with create_client(companion_settings) as client:
        csrf = load_bootstrap(client)
        bootstrap = establish_session(client, csrf)
        health = client.get(
            "/api/v1/health",
            headers={**BOUNDARY_HEADERS, "X-Session-CSRF": bootstrap["csrfToken"]},
        )

    assert health.status_code == 200
    assert health.json()["status"] == "ok"
    assert health.json()["components"] == {
        "database": "ready",
        "contentStore": "ready",
        "worker": "ready",
    }


def test_health_rejects_request_without_session(companion_settings) -> None:
    with create_client(companion_settings) as client:
        response = client.get(
            "/api/v1/health",
            headers={**BOUNDARY_HEADERS, "X-Session-CSRF": "not-a-session"},
        )

    assert response.status_code == 401
    assert response.json()["code"] == "missing_session"


def test_health_rejects_invalid_session(companion_settings) -> None:
    with create_client(companion_settings) as client:
        client.cookies.set(
            "wr_session",
            "invalid",
            domain="word-researcher.localhost",
            path="/api/v1",
        )
        response = client.get(
            "/api/v1/health",
            headers={**BOUNDARY_HEADERS, "X-Session-CSRF": "invalid"},
        )

    assert response.status_code == 401
    assert response.json()["code"] == "invalid_session"


def test_api_rejects_nonlocal_origin(companion_settings) -> None:
    with create_client(companion_settings) as client:
        response = client.get(
            "/api/v1/health",
            headers={"Origin": "https://attacker.example", "Sec-Fetch-Site": "cross-site"},
        )

    assert response.status_code == 403
    assert response.json()["code"] == "local_boundary_rejected"


def test_taskpane_does_not_expose_installation_secret(companion_settings) -> None:
    with create_client(companion_settings) as client:
        response = client.get("/taskpane")

    assert INSTALLATION_SECRET.decode() not in response.text
    assert INSTALLATION_SECRET.decode() not in str(response.request.url)
    assert "HttpOnly" in response.headers["set-cookie"]
    assert "Secure" in response.headers["set-cookie"]


def create_client(settings) -> TestClient:
    app = create_app(settings, INSTALLATION_SECRET)
    return TestClient(
        app,
        base_url="https://word-researcher.localhost:4179",
        client=("127.0.0.1", 50000),
    )


def load_bootstrap(client: TestClient) -> str:
    response = client.get("/taskpane")
    assert response.status_code == 200
    match = re.search(r'content="([^"]+)"', response.text)
    assert match is not None
    return match.group(1)


def establish_session(client: TestClient, csrf: str) -> dict:
    response = client.post(
        "/api/v1/session/bootstrap",
        headers={**BOUNDARY_HEADERS, "X-Bootstrap-CSRF": csrf},
        json={
            "officeHost": "Word",
            "officePlatform": "Mac",
            "wordApi13Supported": True,
        },
    )
    assert response.status_code == 200
    return response.json()
