import os
import uuid
from pathlib import Path

import pytest

from researcher_companion.platform import paths
from researcher_companion.platform.credentials import WindowsCredentialStore

pytestmark = pytest.mark.skipif(os.name != "nt", reason="Windows adapter test")


def test_windows_default_app_data_uses_local_app_data(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))

    assert paths.default_app_data() == tmp_path / "WordResearcher"


def test_windows_credential_manager_round_trip() -> None:
    service = f"WordResearcher.Phase1.Test.{uuid.uuid4()}"
    store = WindowsCredentialStore()
    value = "safe-test-credential-material"

    try:
        store.set(service, "test-account", value)
        assert store.get(service, "test-account") == value
    finally:
        store.delete(service, "test-account")

    assert store.get(service, "test-account") is None
