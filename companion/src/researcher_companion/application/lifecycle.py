from researcher_companion.infrastructure.content_store import LocalContentStore
from researcher_companion.infrastructure.database import SQLiteDatabase
from researcher_companion.infrastructure.worker import SupervisedWorkerShell


class CompanionLifecycle:
    def __init__(
        self,
        database: SQLiteDatabase,
        content_store: LocalContentStore,
        worker: SupervisedWorkerShell,
    ) -> None:
        self._database = database
        self._content_store = content_store
        self._worker = worker

    async def start(self) -> None:
        try:
            self._database.start()
            self._content_store.start()
            await self._worker.start()
        except Exception:
            await self.stop()
            raise

    async def stop(self) -> None:
        await self._worker.stop()
        self._content_store.stop()
        self._database.stop()
