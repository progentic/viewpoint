from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

MAX_API_REQUEST_BYTES = 16_384
BODY_METHODS = {"POST", "PUT", "PATCH"}


class ApiHttpPolicyMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self._app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if not is_api_request(scope):
            await self._app(scope, receive, send)
            return
        bounded_receive = await enforce_request_bound(scope, receive, send)
        if bounded_receive is None:
            return
        await self._app(scope, bounded_receive, no_store_sender(send))


def is_api_request(scope: Scope) -> bool:
    return scope["type"] == "http" and str(scope.get("path", "")).startswith("/api/")


async def enforce_request_bound(
    scope: Scope,
    receive: Receive,
    send: Send,
) -> Receive | None:
    if scope.get("method") not in BODY_METHODS:
        return receive
    body = await read_bounded_body(receive)
    if body is None:
        await reject_oversized_request(scope, receive, send)
        return None
    return replay_body(body)


async def read_bounded_body(receive: Receive) -> bytes | None:
    body = bytearray()
    while True:
        message = await receive()
        if message["type"] == "http.disconnect":
            return bytes(body)
        body.extend(message.get("body", b""))
        if len(body) > MAX_API_REQUEST_BYTES:
            return None
        if not message.get("more_body", False):
            return bytes(body)


def replay_body(body: bytes) -> Receive:
    delivered = False

    async def receive() -> Message:
        nonlocal delivered
        if delivered:
            return {"type": "http.request", "body": b"", "more_body": False}
        delivered = True
        return {"type": "http.request", "body": body, "more_body": False}

    return receive


async def reject_oversized_request(scope: Scope, receive: Receive, send: Send) -> None:
    response = JSONResponse(
        status_code=413,
        content={"code": "request_too_large", "message": "Local request exceeds the limit"},
        headers={"Cache-Control": "no-store"},
    )
    await response(scope, receive, send)


def no_store_sender(send: Send) -> Send:
    async def send_with_policy(message: Message) -> None:
        if message["type"] == "http.response.start":
            headers = list(message.get("headers", []))
            headers.append((b"cache-control", b"no-store"))
            message["headers"] = headers
        await send(message)

    return send_with_policy
