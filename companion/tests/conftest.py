from pathlib import Path

import pytest

from researcher_companion.settings import (
    CompanionSettings,
    LoopbackSettings,
    RuntimePaths,
    SessionSettings,
)


@pytest.fixture
def companion_settings(tmp_path: Path) -> CompanionSettings:
    taskpane = tmp_path / "taskpane"
    assets = taskpane / "assets"
    assets.mkdir(parents=True)
    index = taskpane / "index.html"
    index.write_text(
        '<meta name="word-researcher-bootstrap" content="__BOOTSTRAP_CSRF__">',
        encoding="utf-8",
    )
    return CompanionSettings(
        loopback=LoopbackSettings(),
        session=SessionSettings(bootstrap_ttl_seconds=5, session_ttl_seconds=10),
        paths=RuntimePaths(
            database=tmp_path / "state" / "companion.sqlite3",
            content_store=tmp_path / "content",
            taskpane_index=index,
            taskpane_assets=assets,
            certificate=tmp_path / "tls" / "server-cert.pem",
            private_key=tmp_path / "tls" / "server-key.pem",
            migrations=Path(__file__).resolve().parents[1] / "migrations",
        ),
    )
