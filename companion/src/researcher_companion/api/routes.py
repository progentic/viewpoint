from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends, Header, Request, Response
from fastapi.responses import JSONResponse

from researcher_companion.api.bootstrap_adapter import extract_bootstrap_context
from researcher_companion.api.bootstrap_policy import AuthorizedBootstrapRequest
from researcher_companion.api.errors import BootstrapRejected
from researcher_companion.api.models import (
    ErrorResponse,
    HealthResponse,
    SessionBootstrapRequest,
    SessionBootstrapResponse,
)
from researcher_companion.session import BOOTSTRAP_COOKIE, SESSION_COOKIE

if TYPE_CHECKING:
    from researcher_companion.api.app import ApplicationComponents

ROUTER = APIRouter()


def get_components(request: Request) -> ApplicationComponents:
    return request.app.state.components


def authorize_bootstrap_request(request: Request) -> AuthorizedBootstrapRequest:
    components = get_components(request)
    context = extract_bootstrap_context(request)
    return components.bootstrap.authorize(context)


@ROUTER.get("/taskpane", include_in_schema=False)
async def taskpane(request: Request) -> Response:
    components = get_components(request)
    components.boundary.validate_taskpane(request)
    return components.taskpane.render(components.sessions.issue_bootstrap())


@ROUTER.get("/support", include_in_schema=False)
async def support(request: Request) -> Response:
    components = get_components(request)
    components.boundary.validate_taskpane(request)
    return Response(
        "Word Researcher Phase 1 local connectivity spike.", media_type="text/plain"
    )


@ROUTER.post(
    "/api/v1/session/bootstrap",
    response_model=SessionBootstrapResponse,
    operation_id="bootstrapLocalSession",
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}},
)
async def bootstrap_session(
    request: Request,
    body: SessionBootstrapRequest,
    authorization: Annotated[
        AuthorizedBootstrapRequest,
        Depends(authorize_bootstrap_request),
    ],
    x_bootstrap_csrf: str | None = Header(default=None),
) -> Response:
    del body
    components = get_components(request)
    material = components.bootstrap.establish(
        authorization,
        request.cookies.get(BOOTSTRAP_COOKIE),
        x_bootstrap_csrf,
        request.cookies.get(SESSION_COOKIE),
    )
    return session_response(material)


@ROUTER.api_route(
    "/api/v1/session/bootstrap",
    methods=["GET", "PUT", "PATCH", "DELETE", "OPTIONS"],
    include_in_schema=False,
)
async def reject_bootstrap_method(request: Request) -> None:
    authorize_bootstrap_request(request)
    raise BootstrapRejected("bootstrap_method_invalid")


@ROUTER.api_route(
    "/api/v1/session/{unexpected_path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    include_in_schema=False,
)
async def reject_bootstrap_path(request: Request, unexpected_path: str) -> None:
    del unexpected_path
    authorize_bootstrap_request(request)
    raise BootstrapRejected("bootstrap_path_invalid")


@ROUTER.get(
    "/api/v1/health",
    response_model=HealthResponse,
    operation_id="getHealth",
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}},
)
async def health(
    request: Request,
    x_session_csrf: str | None = Header(default=None),
) -> HealthResponse:
    components = get_components(request)
    components.boundary.validate_api(request)
    components.sessions.validate(request.cookies.get(SESSION_COOKIE), x_session_csrf)
    return components.health.read()


def session_response(material) -> JSONResponse:
    payload = SessionBootstrapResponse(
        csrf_token=material.csrf_token,
        expires_at=material.expires_at,
    ).model_dump(mode="json", by_alias=True)
    response = JSONResponse(payload)
    set_session_cookie(response, material)
    response.delete_cookie(BOOTSTRAP_COOKIE, path="/api/v1/session/bootstrap")
    response.headers["Cache-Control"] = "no-store"
    return response


def set_session_cookie(response: JSONResponse, material) -> None:
    response.set_cookie(
        SESSION_COOKIE,
        material.cookie,
        secure=True,
        httponly=True,
        samesite="strict",
        path="/api/v1",
        expires=material.expires_at,
    )
