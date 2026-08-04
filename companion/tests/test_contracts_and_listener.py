import ipaddress
import socket
import sys
from pathlib import Path

import pytest
from scripts.generate_contracts import build_openapi_contract, serialize_contract

from researcher_companion.infrastructure.port import StablePortGuard
from researcher_companion.install_cli import launch_agent_payload
from researcher_companion.platform.paths import build_runtime_paths
from researcher_companion.settings import LoopbackSettings


def test_openapi_generation_is_deterministic() -> None:
    first = serialize_contract(build_openapi_contract())
    second = serialize_contract(build_openapi_contract())

    assert first == second
    assert '"openapi": "3.1.0"' in first


def test_listener_accepts_only_explicit_ipv4_loopback() -> None:
    LoopbackSettings(bind_host="127.0.0.1").require_loopback()

    with pytest.raises(ValueError, match="loopback"):
        LoopbackSettings(bind_host="0.0.0.0").require_loopback()


def test_stable_port_conflict_fails_closed(monkeypatch) -> None:
    monkeypatch.setattr(socket, "socket", lambda *_arguments: OccupiedSocket())

    with pytest.raises(RuntimeError, match="stop the owner and repair"):
        StablePortGuard().require_available(LoopbackSettings())


def test_generated_outputs_exist() -> None:
    project_root = Path(__file__).resolve().parents[2]

    assert (project_root / "contracts" / "openapi.json").is_file()
    assert (project_root / "taskpane" / "src" / "generated" / "client.ts").is_file()


def test_installed_runtime_paths_do_not_depend_on_project_checkout(tmp_path: Path) -> None:
    runtime_root = tmp_path / "app-data" / "runtime"
    app_data = tmp_path / "app-data"

    paths = build_runtime_paths(runtime_root, app_data)

    assert paths.taskpane_index == runtime_root / "taskpane" / "dist" / "index.html"
    assert paths.migrations == runtime_root / "companion" / "migrations"


def test_launch_agent_uses_staged_runtime_root(tmp_path: Path) -> None:
    runtime_root = tmp_path / "app-data" / "runtime"
    app_data = tmp_path / "app-data"

    payload = launch_agent_payload(tmp_path / "python", runtime_root, app_data)

    assert payload["WorkingDirectory"] == str(runtime_root)
    assert payload["EnvironmentVariables"]["PYTHONPATH"] == str(
        runtime_root / "companion" / "src"
    )


@pytest.mark.skipif(
    sys.platform != "darwin" and sys.platform != "win32",
    reason="Supported desktop resolver test",
)
def test_stable_hostname_resolves_only_to_loopback() -> None:
    addresses = {
        str(item[4][0])
        for item in socket.getaddrinfo(
            "localhost",
            4179,
            type=socket.SOCK_STREAM,
        )
    }

    assert addresses
    assert all(ipaddress.ip_address(address).is_loopback for address in addresses)


class OccupiedSocket:
    def __enter__(self):
        return self

    def __exit__(self, *_arguments) -> None:
        return None

    def bind(self, _address) -> None:
        raise OSError("occupied")
