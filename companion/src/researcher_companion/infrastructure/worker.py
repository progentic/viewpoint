import asyncio
import logging
import sys
from enum import StrEnum

LOGGER = logging.getLogger(__name__)


class WorkerState(StrEnum):
    STOPPED = "stopped"
    READY = "ready"
    FAILED = "failed"


class SupervisedWorkerShell:
    def __init__(self, command: tuple[str, ...] | None = None) -> None:
        self._command = command or (sys.executable, "-m", "researcher_companion.worker_process")
        self._process: asyncio.subprocess.Process | None = None
        self._monitor: asyncio.Task[None] | None = None
        self._state = WorkerState.STOPPED

    async def start(self) -> None:
        if self._process is not None:
            return
        self._process = await asyncio.create_subprocess_exec(
            *self._command,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        self._state = WorkerState.READY
        self._monitor = asyncio.create_task(self._observe_exit())
        LOGGER.info("worker_started")

    async def stop(self) -> None:
        if self._process is None:
            return
        self._state = WorkerState.STOPPED
        await self._terminate_process()
        await self._finish_monitor()
        self._process = None
        LOGGER.info("worker_stopped")

    def is_ready(self) -> bool:
        return self._state == WorkerState.READY

    @property
    def state(self) -> WorkerState:
        return self._state

    async def _observe_exit(self) -> None:
        if self._process is None:
            return
        exit_code = await self._process.wait()
        if self._state == WorkerState.READY:
            self._state = WorkerState.FAILED
            LOGGER.error("worker_failed exit_code=%d", exit_code)

    async def _terminate_process(self) -> None:
        assert self._process is not None
        if self._process.returncode is not None:
            return
        self._process.terminate()
        try:
            await asyncio.wait_for(self._process.wait(), timeout=5)
        except TimeoutError:
            self._process.kill()
            await self._process.wait()

    async def _finish_monitor(self) -> None:
        if self._monitor is not None:
            await self._monitor
            self._monitor = None
