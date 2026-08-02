import socket
from pathlib import Path

import pytest
from scripts.generate_contracts import build_openapi_contract, serialize_contract

from researcher_companion.infrastructure.port import StablePortGuard
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


class OccupiedSocket:
    def __enter__(self):
        return self

    def __exit__(self, *_arguments) -> None:
        return None

    def bind(self, _address) -> None:
        raise OSError("occupied")
