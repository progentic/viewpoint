import argparse
import hashlib
import ipaddress
import json
import os
import socket
import ssl
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMPANION_SOURCE = PROJECT_ROOT / "companion" / "src"
sys.path.insert(0, str(COMPANION_SOURCE))

from researcher_companion.platform.paths import default_app_data
from researcher_companion.settings import STABLE_HOSTNAME, STABLE_PORT

PRODUCTION_ORIGIN = f"https://{STABLE_HOSTNAME}:{STABLE_PORT}"
PRODUCTION_LABEL = "Installed production-origin test."


def main() -> None:
    arguments = parse_arguments()
    result = verify_installed_origin(arguments)
    write_result(arguments.output, result)
    print(json.dumps(result, sort_keys=True))


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify the installed exact HTTPS origin")
    parser.add_argument("--node", default=os.environ.get("PHASE1_NODE_EXECUTABLE", "node"))
    parser.add_argument("--app-data", type=Path, default=configured_app_data())
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def configured_app_data() -> Path:
    configured = os.environ.get("WORD_RESEARCHER_DATA")
    return Path(configured).expanduser() if configured else default_app_data()


def verify_installed_origin(arguments: argparse.Namespace) -> dict:
    root_certificate = arguments.app_data / "tls" / "root-ca.pem"
    require_installed_material(root_certificate)
    addresses = resolve_stable_hostname()
    tls_result = verify_tls(root_certificate)
    curl_result = verify_system_client()
    client_result = run_generated_client(arguments.node, root_certificate)
    return {
        "label": PRODUCTION_LABEL,
        "test": "installed-production-origin",
        "status": "PASS",
        "origin": PRODUCTION_ORIGIN,
        "resolvedAddresses": addresses,
        "tls": tls_result,
        "systemClient": curl_result,
        "generatedClient": client_result,
    }


def require_installed_material(root_certificate: Path) -> None:
    if not root_certificate.is_file():
        raise RuntimeError("Installed root certificate is missing; run the installer")


def resolve_stable_hostname() -> list[str]:
    addresses = sorted(
        {
            str(item[4][0])
            for item in socket.getaddrinfo(
                STABLE_HOSTNAME,
                STABLE_PORT,
                type=socket.SOCK_STREAM,
            )
        }
    )
    if not addresses or not all(ipaddress.ip_address(address).is_loopback for address in addresses):
        raise RuntimeError("Stable hostname did not resolve exclusively to loopback")
    return addresses


def verify_tls(root_certificate: Path) -> dict:
    context = ssl.create_default_context(cafile=str(root_certificate))
    with (
        socket.create_connection((STABLE_HOSTNAME, STABLE_PORT), timeout=5) as raw,
        context.wrap_socket(raw, server_hostname=STABLE_HOSTNAME) as secured,
    ):
        certificate = secured.getpeercert(binary_form=True)
        details = secured.getpeercert()
        peer_address = secured.getpeername()[0]
    if certificate is None or details is None:
        raise RuntimeError("Installed server did not present a verifiable certificate")
    return {
        "certificateSha256": hashlib.sha256(certificate).hexdigest(),
        "peerAddress": peer_address,
        "subjectAltName": details.get("subjectAltName", []),
        "verified": True,
    }


def verify_system_client() -> dict:
    command = [
        "/usr/bin/curl" if sys.platform == "darwin" else "curl.exe",
        "--fail",
        "--silent",
        "--show-error",
        "--noproxy",
        "*",
        "--connect-timeout",
        "5",
        "--max-time",
        "10",
        "--output",
        os.devnull,
        "--write-out",
        "%{http_code}|%{remote_ip}|%{ssl_verify_result}",
        f"{PRODUCTION_ORIGIN}/taskpane",
    ]
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    status, remote_address, tls_result = completed.stdout.split("|")
    if status != "200" or tls_result != "0":
        raise RuntimeError("System HTTPS client did not trust the installed origin")
    return {"httpStatus": int(status), "remoteAddress": remote_address, "tlsResult": 0}


def run_generated_client(node: str, root_certificate: Path) -> dict:
    environment = os.environ.copy()
    environment["PHASE1_PRODUCTION_ORIGIN"] = PRODUCTION_ORIGIN
    environment["NODE_EXTRA_CA_CERTS"] = str(root_certificate)
    command = [
        node,
        "--use-system-ca",
        "node_modules/tsx/dist/cli.mjs",
        "taskpane/tests/generated-client.production-origin.ts",
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
        raise RuntimeError(f"Installed generated client failed: {completed.stderr.strip()}")


if __name__ == "__main__":
    main()
