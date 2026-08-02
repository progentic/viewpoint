import multiprocessing
import os
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMPANION_SOURCE = PROJECT_ROOT / "companion" / "src"
sys.path.insert(0, str(COMPANION_SOURCE))

from researcher_companion.api.app import create_app
from researcher_companion.infrastructure.worker import SupervisedWorkerShell
from researcher_companion.settings import (
    CompanionSettings,
    LoopbackSettings,
    RuntimePaths,
    SessionSettings,
)

ORIGIN = "https://127.0.0.1:4179"
TRANSPORT_ORIGIN = "http://127.0.0.1:4179"


def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        runtime = Path(directory)
        settings = integration_settings(runtime)
        server = multiprocessing.Process(target=run_server, args=(settings,), daemon=True)
        server.start()
        try:
            wait_until_ready()
            run_generated_client()
        finally:
            server.terminate()
            server.join(timeout=5)


def integration_settings(runtime: Path) -> CompanionSettings:
    return CompanionSettings(
        loopback=LoopbackSettings(hostname="127.0.0.1"),
        session=SessionSettings(),
        paths=RuntimePaths(
            database=runtime / "state" / "companion.sqlite3",
            content_store=runtime / "content",
            taskpane_index=PROJECT_ROOT / "taskpane" / "dist" / "index.html",
            taskpane_assets=PROJECT_ROOT / "taskpane" / "dist" / "assets",
            certificate=runtime / "tls" / "server-cert.pem",
            private_key=runtime / "tls" / "server-key.pem",
            migrations=PROJECT_ROOT / "companion" / "migrations",
        ),
    )


def run_server(settings: CompanionSettings) -> None:
    import uvicorn

    worker = SupervisedWorkerShell((sys.executable, "-c", "import time; time.sleep(60)"))
    application = create_app(settings, os.urandom(48), worker)
    uvicorn.run(
        application,
        host=settings.loopback.bind_host,
        port=settings.loopback.port,
        access_log=False,
        proxy_headers=False,
        server_header=False,
        log_level="warning",
    )


def wait_until_ready() -> None:
    for _attempt in range(100):
        try:
            with socket.create_connection(("127.0.0.1", 4179), timeout=0.2):
                return
        except OSError:
            time.sleep(0.05)
    raise RuntimeError("Local companion integration listener did not become ready")


def run_generated_client() -> None:
    environment = os.environ.copy()
    environment["PHASE1_ORIGIN"] = ORIGIN
    environment["PHASE1_TRANSPORT_ORIGIN"] = TRANSPORT_ORIGIN
    node_executable = environment.get("PHASE1_NODE_EXECUTABLE", "node")
    subprocess.run(
        [node_executable, "node_modules/tsx/dist/cli.mjs", "taskpane/tests/generated-client.roundtrip.ts"],
        cwd=PROJECT_ROOT,
        env=environment,
        check=True,
    )


if __name__ == "__main__":
    main()
