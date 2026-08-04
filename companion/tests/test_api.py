import re
from pathlib import Path

from fastapi.testclient import TestClient
from httpx import Response

from researcher_companion.api.app import create_app
from researcher_companion.api.http_policy import MAX_API_REQUEST_BYTES

BOUNDARY_HEADERS = {
    "Origin": "https://localhost:4179",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
}
MISSING_ORIGIN_PROFILE_HEADERS = {
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
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


def test_health_accepts_missing_origin_after_valid_local_session(
    companion_settings,
) -> None:
    with create_client(companion_settings) as client:
        csrf = load_bootstrap(client)
        bootstrap = establish_session(client, csrf, MISSING_ORIGIN_PROFILE_HEADERS)
        health = client.get(
            "/api/v1/health",
            headers={
                **MISSING_ORIGIN_PROFILE_HEADERS,
                "X-Session-CSRF": bootstrap["csrfToken"],
            },
        )

    assert health.status_code == 200
    assert health.json()["status"] == "ok"


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


def test_bootstrap_accepts_verified_missing_origin_profile(companion_settings) -> None:
    with create_client(companion_settings) as client:
        csrf = load_bootstrap(client)
        bootstrap = establish_session(client, csrf, MISSING_ORIGIN_PROFILE_HEADERS)

    assert bootstrap["csrfToken"]


def test_bootstrap_rejects_unexpected_origin(companion_settings) -> None:
    with create_client(companion_settings) as client:
        csrf = load_bootstrap(client)
        response = post_bootstrap(
            client,
            csrf,
            {
                "Origin": "https://attacker.example",
                "Sec-Fetch-Site": "cross-site",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
            },
        )

    assert response.status_code == 403
    assert response.json()["code"] == "bootstrap_origin_unexpected"


def test_bootstrap_rejects_missing_origin_without_complete_profile(
    companion_settings,
) -> None:
    with create_client(companion_settings) as client:
        csrf = load_bootstrap(client)
        response = post_bootstrap(
            client,
            csrf,
            {"Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "cors"},
        )

    assert response.status_code == 403
    assert response.json()["code"] == "bootstrap_fetch_metadata_invalid"


def test_bootstrap_rejects_wrong_content_type_before_body_validation(
    companion_settings,
) -> None:
    with create_client(companion_settings) as client:
        csrf = load_bootstrap(client)
        response = client.post(
            "/api/v1/session/bootstrap",
            headers={
                **MISSING_ORIGIN_PROFILE_HEADERS,
                "Content-Type": "text/plain",
                "X-Bootstrap-CSRF": csrf,
            },
            content='{"officeHost":"Word","officePlatform":"Mac",'
            '"wordApi13Supported":true}',
        )

    assert response.status_code == 403
    assert response.json()["code"] == "bootstrap_content_type_invalid"


def test_bootstrap_rejects_wrong_method_and_path_with_safe_codes(
    companion_settings,
) -> None:
    with create_client(companion_settings) as client:
        wrong_method = client.get("/api/v1/session/bootstrap")
        wrong_path = client.post(
            "/api/v1/session/not-bootstrap",
            headers=MISSING_ORIGIN_PROFILE_HEADERS,
            json={},
        )

    assert wrong_method.status_code == 403
    assert wrong_method.json()["code"] == "bootstrap_method_invalid"
    assert wrong_path.status_code == 403
    assert wrong_path.json()["code"] == "bootstrap_path_invalid"


def test_api_rejects_foreign_host(companion_settings) -> None:
    with create_client(companion_settings) as client:
        response = client.get(
            "/api/v1/health",
            headers={**BOUNDARY_HEADERS, "Host": "attacker.example"},
        )

    assert response.status_code == 403
    assert response.json()["code"] == "local_boundary_rejected"


def test_bootstrap_rejects_foreign_host_with_specific_code(companion_settings) -> None:
    with create_client(companion_settings) as client:
        csrf = load_bootstrap(client)
        response = post_bootstrap(
            client,
            csrf,
            {**MISSING_ORIGIN_PROFILE_HEADERS, "Host": "127.0.0.1:4179"},
        )

    assert response.status_code == 403
    assert response.json()["code"] == "bootstrap_host_invalid"


def test_api_rejects_absent_or_invalid_fetch_site(caplog, companion_settings) -> None:
    with create_client(companion_settings) as client:
        absent = client.get("/api/v1/health", headers={"Origin": BOUNDARY_HEADERS["Origin"]})
        invalid = client.get(
            "/api/v1/health",
            headers={"Origin": BOUNDARY_HEADERS["Origin"], "Sec-Fetch-Site": "cross-site"},
        )

    assert absent.status_code == 403
    assert invalid.status_code == 403
    assert "reason=browser_context origin=exact fetch_site=missing" in caplog.text
    assert "reason=browser_context origin=exact fetch_site=cross-site" in caplog.text
    assert BOUNDARY_HEADERS["Origin"] not in caplog.text


def test_api_rejects_nonloopback_client(companion_settings) -> None:
    app = create_app(companion_settings, INSTALLATION_SECRET)
    with TestClient(
        app,
        base_url="https://localhost:4179",
        client=("192.0.2.10", 50000),
    ) as client:
        response = client.get("/taskpane")

    assert response.status_code == 403
    assert response.json()["code"] == "local_boundary_rejected"


def test_api_rejects_oversized_request_before_parsing(companion_settings) -> None:
    with create_client(companion_settings) as client:
        response = client.post(
            "/api/v1/session/bootstrap",
            headers=BOUNDARY_HEADERS,
            content=b"x" * (MAX_API_REQUEST_BYTES + 1),
        )

    assert response.status_code == 413
    assert response.json()["code"] == "request_too_large"
    assert response.headers["Cache-Control"] == "no-store"


def test_api_responses_are_not_cacheable_or_redirected(companion_settings) -> None:
    with create_client(companion_settings) as client:
        csrf = load_bootstrap(client)
        bootstrap = establish_session(client, csrf)
        health = client.get(
            "/api/v1/health",
            headers={**BOUNDARY_HEADERS, "X-Session-CSRF": bootstrap["csrfToken"]},
            follow_redirects=False,
        )

    assert health.status_code == 200
    assert health.headers["Cache-Control"] == "no-store"
    assert "location" not in health.headers


def test_bootstrap_cannot_be_replayed(companion_settings) -> None:
    with create_client(companion_settings) as client:
        csrf = load_bootstrap(client)
        challenge = client.cookies.get("wr_bootstrap")
        establish_session(client, csrf)
        client.cookies.set(
            "wr_bootstrap",
            challenge,
            path="/api/v1/session/bootstrap",
        )
        replay = client.post(
            "/api/v1/session/bootstrap",
            headers={**BOUNDARY_HEADERS, "X-Bootstrap-CSRF": csrf},
            json={
                "officeHost": "Word",
                "officePlatform": "Mac",
                "wordApi13Supported": True,
            },
        )

    assert replay.status_code == 403
    assert replay.json()["code"] == "bootstrap_replay_rejected"


def test_bootstrap_rotates_session_and_invalidates_prior_cookie(companion_settings) -> None:
    with create_client(companion_settings) as client:
        first_csrf = load_bootstrap(client)
        first_session = establish_session(client, first_csrf)
        first_cookie = client.cookies.get("wr_session")
        second_csrf = load_bootstrap(client)
        second_session = establish_session(client, second_csrf)
        second_cookie = client.cookies.get("wr_session")
        client.cookies.set("wr_session", first_cookie, path="/api/v1")
        rejected = client.get(
            "/api/v1/health",
            headers={**BOUNDARY_HEADERS, "X-Session-CSRF": first_session["csrfToken"]},
        )

    assert first_cookie != second_cookie
    assert first_session["csrfToken"] != second_session["csrfToken"]
    assert rejected.status_code == 401
    assert rejected.json()["code"] == "invalid_session"


def test_bootstrap_session_cookie_has_required_attributes(companion_settings) -> None:
    with create_client(companion_settings) as client:
        csrf = load_bootstrap(client)
        response = post_bootstrap(client, csrf, BOUNDARY_HEADERS)

    cookie = response.headers["set-cookie"].lower()
    assert response.status_code == 200
    assert "secure" in cookie
    assert "httponly" in cookie
    assert "samesite=strict" in cookie
    assert "path=/api/v1" in cookie


def test_hostile_browser_profiles_fail_closed(companion_settings) -> None:
    with create_client(companion_settings) as client:
        csrf = load_bootstrap(client)
        attempts = hostile_browser_attempts(client, csrf)

    assert all(response.status_code >= 400 for response in attempts.values())
    assert attempts["preflight"].headers.get("access-control-allow-origin") is None
    assert attempts["foreign_fetch"].json()["code"] == "bootstrap_origin_unexpected"
    assert attempts["form_post"].json()["code"] == "bootstrap_origin_unexpected"
    assert attempts["missing_metadata"].json()["code"] == "bootstrap_fetch_metadata_invalid"


def hostile_browser_attempts(client: TestClient, csrf: str) -> dict[str, Response]:
    foreign = {
        "Origin": "https://attacker.example",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
    }
    return {
        "foreign_fetch": post_bootstrap(client, csrf, foreign),
        "form_post": client.post(
            "/api/v1/session/bootstrap",
            headers={**foreign, "Content-Type": "application/x-www-form-urlencoded"},
            content="officeHost=Word",
        ),
        "simple_request": post_bootstrap(client, csrf, foreign),
        "preflight": client.options(
            "/api/v1/session/bootstrap",
            headers={
                **foreign,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type,x-bootstrap-csrf",
            },
        ),
        "navigation": client.get("/api/v1/session/bootstrap"),
        "missing_metadata": post_bootstrap(client, csrf, {}),
        "forged_incomplete": post_bootstrap(
            client,
            csrf,
            {"Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "cors"},
        ),
    }


def test_taskpane_does_not_expose_installation_secret(companion_settings) -> None:
    with create_client(companion_settings) as client:
        response = client.get("/taskpane")

    assert INSTALLATION_SECRET.decode() not in response.text
    assert INSTALLATION_SECRET.decode() not in str(response.request.url)
    assert "HttpOnly" in response.headers["set-cookie"]
    assert "Secure" in response.headers["set-cookie"]
    assert response.headers["Cache-Control"] == "no-store"
    assert "location" not in response.headers


def test_installation_secret_is_absent_from_sqlite_and_browser_storage(
    companion_settings,
) -> None:
    with create_client(companion_settings) as client:
        csrf = load_bootstrap(client)
        establish_session(client, csrf)

    assert INSTALLATION_SECRET not in companion_settings.paths.database.read_bytes()
    taskpane_source = Path(__file__).resolve().parents[2] / "taskpane" / "src"
    browser_code = "\n".join(
        path.read_text(encoding="utf-8") for path in taskpane_source.rglob("*.ts*")
    )
    assert "localStorage" not in browser_code
    assert "sessionStorage" not in browser_code


def test_installation_secret_is_absent_from_logs(caplog, companion_settings) -> None:
    with create_client(companion_settings) as client:
        csrf = load_bootstrap(client)
        bootstrap = establish_session(client, csrf)
        client.get(
            "/api/v1/health",
            headers={**BOUNDARY_HEADERS, "X-Session-CSRF": bootstrap["csrfToken"]},
        )

    assert INSTALLATION_SECRET.decode() not in caplog.text


def create_client(settings) -> TestClient:
    app = create_app(settings, INSTALLATION_SECRET)
    return TestClient(
        app,
        base_url="https://localhost:4179",
        client=("127.0.0.1", 50000),
    )


def load_bootstrap(client: TestClient) -> str:
    response = client.get("/taskpane")
    assert response.status_code == 200
    match = re.search(r'content="([^"]+)"', response.text)
    assert match is not None
    return match.group(1)


def establish_session(
    client: TestClient,
    csrf: str,
    boundary_headers: dict[str, str] | None = None,
) -> dict:
    response = post_bootstrap(client, csrf, boundary_headers or BOUNDARY_HEADERS)
    assert response.status_code == 200
    return response.json()


def post_bootstrap(client: TestClient, csrf: str, headers: dict[str, str]) -> Response:
    return client.post(
        "/api/v1/session/bootstrap",
        headers={**headers, "X-Bootstrap-CSRF": csrf},
        json={
            "officeHost": "Word",
            "officePlatform": "Mac",
            "wordApi13Supported": True,
        },
    )
