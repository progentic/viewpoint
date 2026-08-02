from researcher_companion import __version__
from researcher_companion.api.models import ComponentHealth, HealthResponse
from researcher_companion.infrastructure.content_store import LocalContentStore
from researcher_companion.infrastructure.database import SQLiteDatabase
from researcher_companion.infrastructure.worker import SupervisedWorkerShell


class HealthService:
    def __init__(
        self,
        database: SQLiteDatabase,
        content_store: LocalContentStore,
        worker: SupervisedWorkerShell,
    ) -> None:
        self._database = database
        self._content_store = content_store
        self._worker = worker

    def read(self) -> HealthResponse:
        self._require_ready_components()
        return HealthResponse(
            version=__version__,
            components=ComponentHealth(database="ready", content_store="ready", worker="ready"),
        )

    def _require_ready_components(self) -> None:
        if not self._database.is_ready():
            raise RuntimeError("Database is not ready")
        if not self._content_store.is_ready():
            raise RuntimeError("Content store is not ready")
        if not self._worker.is_ready():
            raise RuntimeError("Worker is not ready")
