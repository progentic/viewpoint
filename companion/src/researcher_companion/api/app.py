from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from researcher_companion.api.boundary import LocalRequestBoundary
from researcher_companion.api.errors import BoundaryRejected, SessionRejected
from researcher_companion.api.models import (
    ErrorResponse,
)
from researcher_companion.api.routes import ROUTER
from researcher_companion.api.taskpane import TaskPaneRenderer
from researcher_companion.application.health import HealthService
from researcher_companion.application.lifecycle import CompanionLifecycle
from researcher_companion.clock import SystemClock
from researcher_companion.infrastructure.content_store import LocalContentStore
from researcher_companion.infrastructure.database import SQLiteDatabase
from researcher_companion.infrastructure.worker import SupervisedWorkerShell
from researcher_companion.session import LocalSessionManager
from researcher_companion.settings import CompanionSettings


@dataclass(frozen=True)
class ApplicationComponents:
    boundary: LocalRequestBoundary
    health: HealthService
    lifecycle: CompanionLifecycle
    sessions: LocalSessionManager
    taskpane: TaskPaneRenderer


def create_app(
    settings: CompanionSettings,
    installation_secret: bytes,
    worker: SupervisedWorkerShell | None = None,
) -> FastAPI:
    settings.validate()
    components = compose_components(settings, installation_secret, worker)
    app = FastAPI(
        title="Word Researcher Local Companion",
        version="0.1.0",
        openapi_version="3.1.0",
        docs_url=None,
        redoc_url=None,
        lifespan=create_lifespan(components.lifecycle),
    )
    app.state.components = components
    register_error_handlers(app)
    app.include_router(ROUTER)
    register_static_assets(app, settings)
    return app


def compose_components(
    settings: CompanionSettings,
    installation_secret: bytes,
    worker: SupervisedWorkerShell | None,
) -> ApplicationComponents:
    database = SQLiteDatabase(settings.paths.database, settings.paths.migrations)
    content_store = LocalContentStore(settings.paths.content_store)
    worker_shell = worker or SupervisedWorkerShell()
    return ApplicationComponents(
        boundary=LocalRequestBoundary(settings.loopback),
        health=HealthService(database, content_store, worker_shell),
        lifecycle=CompanionLifecycle(database, content_store, worker_shell),
        sessions=LocalSessionManager(installation_secret, settings.session, SystemClock()),
        taskpane=TaskPaneRenderer(settings.paths.taskpane_index),
    )


def create_lifespan(lifecycle: CompanionLifecycle):
    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        await lifecycle.start()
        try:
            yield
        finally:
            await lifecycle.stop()

    return lifespan


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(SessionRejected)
    async def handle_session_rejection(_request: Request, error: SessionRejected) -> JSONResponse:
        content = ErrorResponse(code=error.code, message=error.message).model_dump(by_alias=True)
        return JSONResponse(status_code=401, content=content)

    @app.exception_handler(BoundaryRejected)
    async def handle_boundary_rejection(_request: Request, error: BoundaryRejected) -> JSONResponse:
        content = ErrorResponse(code="local_boundary_rejected", message=str(error)).model_dump(
            by_alias=True
        )
        return JSONResponse(status_code=403, content=content)


def register_static_assets(app: FastAPI, settings: CompanionSettings) -> None:
    app.mount(
        "/assets",
        StaticFiles(directory=settings.paths.taskpane_assets, check_dir=False),
        name="taskpane-assets",
    )
