import ipaddress

from fastapi import Request

from researcher_companion.api.errors import BoundaryRejected
from researcher_companion.settings import LoopbackSettings


class LocalRequestBoundary:
    def __init__(self, settings: LoopbackSettings) -> None:
        self._settings = settings

    def validate_taskpane(self, request: Request) -> None:
        self._validate_authority(request)
        self._validate_client(request)

    def validate_api(self, request: Request) -> None:
        self.validate_taskpane(request)
        self._validate_origin(request)
        self._validate_fetch_site(request)

    def _validate_authority(self, request: Request) -> None:
        if request.headers.get("host") != self._settings.authority:
            raise BoundaryRejected("Request host does not match the installed local origin")

    def _validate_client(self, request: Request) -> None:
        client = request.client
        if client is None or not self._is_loopback(client.host):
            raise BoundaryRejected("The companion accepts loopback clients only")

    def _validate_origin(self, request: Request) -> None:
        if request.headers.get("origin") != self._settings.origin:
            raise BoundaryRejected("Request origin does not match the installed task pane")

    def _validate_fetch_site(self, request: Request) -> None:
        if request.headers.get("sec-fetch-site") != "same-origin":
            raise BoundaryRejected("Request was not initiated by the local task pane origin")

    def _is_loopback(self, host: str) -> bool:
        try:
            return ipaddress.ip_address(host).is_loopback
        except ValueError:
            return False
