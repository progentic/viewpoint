from datetime import UTC, datetime, timedelta

import pytest

from researcher_companion.api.errors import SessionRejected
from researcher_companion.session import LocalSessionManager
from researcher_companion.settings import SessionSettings


class MutableClock:
    def __init__(self) -> None:
        self.current = datetime(2026, 8, 1, tzinfo=UTC)

    def now(self) -> datetime:
        return self.current

    def advance(self, seconds: int) -> None:
        self.current += timedelta(seconds=seconds)


def test_expired_bootstrap_is_rejected() -> None:
    manager, clock = create_manager()
    bootstrap = manager.issue_bootstrap()
    clock.advance(6)

    with pytest.raises(SessionRejected, match="Reload") as rejection:
        manager.establish(bootstrap.cookie, bootstrap.csrf_token)

    assert rejection.value.code == "expired_bootstrap"


def test_invalid_bootstrap_is_rejected() -> None:
    manager, _clock = create_manager()
    bootstrap = manager.issue_bootstrap()

    with pytest.raises(SessionRejected) as rejection:
        manager.establish(bootstrap.cookie, "wrong-token")

    assert rejection.value.code == "invalid_bootstrap"


def test_expired_session_is_rejected() -> None:
    manager, clock = create_manager()
    bootstrap = manager.issue_bootstrap()
    session = manager.establish(bootstrap.cookie, bootstrap.csrf_token)
    clock.advance(11)

    with pytest.raises(SessionRejected) as rejection:
        manager.validate(session.cookie, session.csrf_token)

    assert rejection.value.code == "expired_session"


def create_manager() -> tuple[LocalSessionManager, MutableClock]:
    clock = MutableClock()
    manager = LocalSessionManager(
        b"test-installation-secret-with-at-least-32-bytes",
        SessionSettings(bootstrap_ttl_seconds=5, session_ttl_seconds=10),
        clock,
    )
    return manager, clock
