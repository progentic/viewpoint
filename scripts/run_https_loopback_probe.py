import json
import multiprocessing
import os
import socket
import ssl
import sys
import tempfile
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMPANION_SOURCE = PROJECT_ROOT / "companion" / "src"
sys.path.insert(0, str(COMPANION_SOURCE))

from researcher_companion.api.app import create_app
from researcher_companion.infrastructure.worker import SupervisedWorkerShell
from researcher_companion.platform.tls import PerInstallTlsProvisioner
from researcher_companion.settings import (
    CompanionSettings,
    LoopbackSettings,
    RuntimePaths,
    SessionSettings,
)


def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        runtime = Path(directory)
        settings = probe_settings(runtime)
        tls = PerInstallTlsProvisioner(runtime / "tls", settings.loopback.hostname).provision()
        server = multiprocessing.Process(target=run_server, args=(settings,), daemon=True)
        server.start()
        try:
            response, observation = wait_for_https_response(settings, tls.root_certificate)
            validate_response(response)
        finally:
            server.terminate()
            server.join(timeout=5)
    print(
        json.dumps(
            {
                "label": "HTTPS bind and certificate test.",
                "test": "https-bind-and-certificate",
                "status": "PASS",
                "httpStatus": 200,
                **observation,
            },
            sort_keys=True,
        )
    )


def probe_settings(runtime: Path) -> CompanionSettings:
    return CompanionSettings(
        loopback=LoopbackSettings(),
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
        ssl_certfile=str(settings.paths.certificate),
        ssl_keyfile=str(settings.paths.private_key),
        access_log=False,
        proxy_headers=False,
        server_header=False,
        log_level="warning",
    )


def wait_for_https_response(
    settings: CompanionSettings,
    root_certificate: Path,
) -> tuple[bytes, dict[str, object]]:
    context = ssl.create_default_context(cafile=str(root_certificate))
    for _attempt in range(100):
        try:
            return request_taskpane(settings, context)
        except OSError:
            time.sleep(0.05)
    raise RuntimeError("Trusted local HTTPS listener did not become ready")


def request_taskpane(
    settings: CompanionSettings,
    context: ssl.SSLContext,
) -> tuple[bytes, dict[str, object]]:
    connection = (settings.loopback.bind_host, settings.loopback.port)
    with (
        socket.create_connection(connection, 0.2) as raw,
        context.wrap_socket(raw, server_hostname=settings.loopback.hostname) as secured,
    ):
        observation = tls_observation(settings, secured)
        secured.sendall(http_request(settings.loopback.authority))
        return receive_response(secured), observation


def tls_observation(settings: CompanionSettings, connection: ssl.SSLSocket) -> dict[str, object]:
    certificate = connection.getpeercert()
    if certificate is None:
        raise RuntimeError("Local TLS listener did not present a certificate")
    return {
        "authority": settings.loopback.authority,
        "bindAddress": settings.loopback.bind_host,
        "peerAddress": connection.getpeername()[0],
        "subjectAltName": certificate.get("subjectAltName", []),
        "tlsVerified": True,
    }


def http_request(authority: str) -> bytes:
    return (
        f"GET /taskpane HTTP/1.1\r\nHost: {authority}\r\nConnection: close\r\n\r\n"
    ).encode()


def receive_response(connection: ssl.SSLSocket) -> bytes:
    chunks = []
    while chunk := connection.recv(8192):
        chunks.append(chunk)
    return b"".join(chunks)


def validate_response(response: bytes) -> None:
    if b"HTTP/1.1 200 OK" not in response:
        raise RuntimeError("Trusted local HTTPS request did not return the task pane")
    if b"https://appsforoffice.microsoft.com/lib/1/hosted/office.js" not in response:
        raise RuntimeError("Task pane did not load production Office.js")


if __name__ == "__main__":
    main()
