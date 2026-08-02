import os
import sys
from pathlib import Path

from researcher_companion.settings import CompanionSettings, LoopbackSettings, RuntimePaths


def load_companion_settings() -> CompanionSettings:
    project_root = Path(__file__).resolve().parents[4]
    app_data = configured_app_data() or default_app_data()
    return CompanionSettings(
        loopback=LoopbackSettings(),
        session=default_session_settings(),
        paths=build_runtime_paths(project_root, app_data),
    )


def configured_app_data() -> Path | None:
    configured = os.environ.get("WORD_RESEARCHER_DATA")
    return Path(configured).expanduser() if configured else None


def default_app_data() -> Path:
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "WordResearcher"
    if os.name == "nt":
        return Path(os.environ["LOCALAPPDATA"]) / "WordResearcher"
    raise RuntimeError("Phase 1 companion supports only macOS and Windows")


def default_session_settings():
    from researcher_companion.settings import SessionSettings

    return SessionSettings()


def build_runtime_paths(project_root: Path, app_data: Path) -> RuntimePaths:
    return RuntimePaths(
        database=app_data / "state" / "companion.sqlite3",
        content_store=app_data / "content",
        taskpane_index=project_root / "taskpane" / "dist" / "index.html",
        taskpane_assets=project_root / "taskpane" / "dist" / "assets",
        certificate=app_data / "tls" / "server-cert.pem",
        private_key=app_data / "tls" / "server-key.pem",
        migrations=project_root / "companion" / "migrations",
    )
