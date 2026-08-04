import argparse
import json
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
from researcher_companion.api.bootstrap_policy import (
    BootstrapRequestPolicy,
    EmbeddedHostProfile,
)
from researcher_companion.infrastructure.worker import SupervisedWorkerShell
from researcher_companion.settings import (
    CompanionSettings,
    LoopbackSettings,
    RuntimePaths,
    SessionSettings,
)

PROTOCOL_LOGICAL_ORIGIN = "https://127.0.0.1:4179"
PROTOCOL_TRANSPORT_ORIGIN = "http://127.0.0.1:4179"
PROTOCOL_LABEL = "Generated-client protocol round trip under test transport."


def main() -> None:
    arguments = parse_arguments()
    with tempfile.TemporaryDirectory() as directory:
        settings = protocol_settings(Path(directory))
        server = start_server(settings)
        try:
            wait_until_ready()
            result = run_generated_client(arguments.node)
            result["label"] = PROTOCOL_LABEL
            write_result(arguments.output, result)
        finally:
            stop_server(server)
    print(json.dumps(result, sort_keys=True))


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run generated client under test transport")
    parser.add_argument("--node", default=os.environ.get("PHASE1_NODE_EXECUTABLE", "node"))
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def protocol_settings(runtime: Path) -> CompanionSettings:
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


def start_server(settings: CompanionSettings) -> multiprocessing.Process:
    server = multiprocessing.Process(target=run_server, args=(settings,), daemon=True)
    server.start()
    return server


def run_server(settings: CompanionSettings) -> None:
    import uvicorn

    worker = SupervisedWorkerShell((sys.executable, "-c", "import time; time.sleep(60)"))
    application = create_app(
        settings,
        os.urandom(48),
        worker,
        protocol_bootstrap_policy(settings),
    )
    uvicorn.run(
        application,
        host=settings.loopback.bind_host,
        port=settings.loopback.port,
        access_log=False,
        proxy_headers=False,
        server_header=False,
        log_level="warning",
    )


def protocol_bootstrap_policy(settings: CompanionSettings) -> BootstrapRequestPolicy:
    profile = EmbeddedHostProfile(
        profile_id="protocol-test-transport",
        host=settings.loopback.authority,
        origin=PROTOCOL_LOGICAL_ORIGIN,
        scheme="http",
        method="POST",
        path="/api/v1/session/bootstrap",
        content_type="application/json",
        fetch_site="same-origin",
        fetch_mode="cors",
        fetch_destination="empty",
    )
    return BootstrapRequestPolicy(profile)


def wait_until_ready() -> None:
    for _attempt in range(100):
        try:
            with socket.create_connection(("127.0.0.1", 4179), timeout=0.2):
                return
        except OSError:
            time.sleep(0.05)
    raise RuntimeError("Protocol test listener did not become ready")


def run_generated_client(node: str) -> dict:
    environment = os.environ.copy()
    environment["PHASE1_PROTOCOL_LOGICAL_ORIGIN"] = PROTOCOL_LOGICAL_ORIGIN
    environment["PHASE1_PROTOCOL_TRANSPORT_ORIGIN"] = PROTOCOL_TRANSPORT_ORIGIN
    command = [
        node,
        "node_modules/tsx/dist/cli.mjs",
        "taskpane/tests/generated-client.protocol.ts",
    ]
    completed = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    require_success(completed)
    return json.loads(completed.stdout.strip().splitlines()[-1])


def write_result(output: Path | None, result: dict) -> None:
    if output is None:
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def require_success(completed: subprocess.CompletedProcess[str]) -> None:
    if completed.returncode != 0:
        raise RuntimeError(f"Generated protocol client failed: {completed.stderr.strip()}")


def stop_server(server: multiprocessing.Process) -> None:
    server.terminate()
    server.join(timeout=5)


if __name__ == "__main__":
    main()
