import asyncio
import os
import sys
from pathlib import Path

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes

from researcher_companion.infrastructure.content_store import LocalContentStore
from researcher_companion.infrastructure.database import SQLiteDatabase
from researcher_companion.infrastructure.worker import SupervisedWorkerShell, WorkerState
from researcher_companion.platform.credentials import (
    InMemoryCredentialStore,
    InstallationSecretService,
)
from researcher_companion.platform.tls import PerInstallTlsProvisioner


def test_fresh_database_runs_initial_migration(tmp_path: Path) -> None:
    migrations = Path(__file__).resolve().parents[1] / "migrations"
    database = SQLiteDatabase(tmp_path / "state.sqlite3", migrations)

    database.start()
    applied = database.applied_migrations()
    database.stop()

    assert applied == ["0001_phase1_runtime.sql"]


def test_content_store_boundary_initializes_private_directory(tmp_path: Path) -> None:
    store = LocalContentStore(tmp_path / "content")

    store.start()

    assert store.is_ready()
    assert os.stat(store.root).st_mode & 0o777 == 0o700
    store.stop()


def test_worker_starts_and_stops() -> None:
    async def scenario() -> None:
        worker = SupervisedWorkerShell()
        await worker.start()
        assert worker.state == WorkerState.READY
        await worker.stop()
        assert worker.state == WorkerState.STOPPED

    asyncio.run(scenario())


def test_worker_supervises_unexpected_failure() -> None:
    async def scenario() -> None:
        worker = SupervisedWorkerShell((sys.executable, "-c", "raise SystemExit(7)"))
        await worker.start()
        await wait_for_failure(worker)
        assert worker.state == WorkerState.FAILED
        await worker.stop()

    asyncio.run(scenario())


def test_installation_secret_is_generated_in_credential_store() -> None:
    store = InMemoryCredentialStore()
    service = InstallationSecretService(store)

    first = service.ensure()
    second = service.ensure()

    assert first == second
    assert len(first) >= 32


def test_missing_installation_secret_fails_closed() -> None:
    service = InstallationSecretService(InMemoryCredentialStore())

    with pytest.raises(RuntimeError, match="installer repair"):
        service.load()


def test_invalid_stored_installation_secret_fails_closed() -> None:
    store = InMemoryCredentialStore()
    store.set("WordResearcher.Phase1", "installation-secret", "too-short")

    with pytest.raises(RuntimeError, match="reinstall"):
        InstallationSecretService(store).load()


def test_invalid_installation_secret_is_rejected_by_session_boundary(companion_settings) -> None:
    from researcher_companion.api.app import create_app

    with pytest.raises(ValueError, match="at least 32 bytes"):
        create_app(companion_settings, b"too-short")


def test_tls_material_is_unique_and_scoped_to_stable_hostname(tmp_path: Path) -> None:
    first = PerInstallTlsProvisioner(tmp_path / "first", "localhost").provision()
    second = PerInstallTlsProvisioner(tmp_path / "second", "localhost").provision()
    first_certificate = x509.load_pem_x509_certificate(first.server_certificate.read_bytes())
    second_certificate = x509.load_pem_x509_certificate(second.server_certificate.read_bytes())

    assert first_certificate.fingerprint(hashes.SHA256()) != second_certificate.fingerprint(
        hashes.SHA256()
    )
    names = first_certificate.extensions.get_extension_for_class(x509.SubjectAlternativeName).value
    assert names.get_values_for_type(x509.DNSName) == ["localhost"]
    assert os.stat(first.server_private_key).st_mode & 0o777 == 0o600


async def wait_for_failure(worker: SupervisedWorkerShell) -> None:
    for _attempt in range(100):
        if worker.state == WorkerState.FAILED:
            return
        await asyncio.sleep(0.01)
    pytest.fail("Worker failure was not observed")
