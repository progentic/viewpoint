import ipaddress
from dataclasses import dataclass

from fastapi import Request

from researcher_companion.api.errors import BoundaryRejected
from researcher_companion.settings import LoopbackSettings

KNOWN_FETCH_SITES = {"same-origin", "same-site", "cross-site", "none"}
KNOWN_FETCH_MODES = {"cors", "navigate", "no-cors", "same-origin", "websocket"}
KNOWN_FETCH_DESTINATIONS = {"document", "empty", "iframe", "script", "style"}


@dataclass(frozen=True)
class BrowserContextObservation:
    origin: str
    fetch_site: str
    fetch_mode: str
    fetch_destination: str

    def is_allowed(self) -> bool:
        return (
            self.origin in {"exact", "missing"}
            and self.fetch_site == "same-origin"
            and self.fetch_mode == "cors"
            and self.fetch_destination == "empty"
        )

    def safe_reason(self) -> str:
        return (
            f"browser_context origin={self.origin} fetch_site={self.fetch_site} "
            f"fetch_mode={self.fetch_mode} fetch_destination={self.fetch_destination}"
        )


class LocalRequestBoundary:
    def __init__(self, settings: LoopbackSettings) -> None:
        self._settings = settings

    def validate_taskpane(self, request: Request) -> None:
        self._validate_authority(request)
        self._validate_client(request)

    def validate_api(self, request: Request) -> None:
        self.validate_taskpane(request)
        self._validate_browser_context(request)

    def _validate_authority(self, request: Request) -> None:
        if request.headers.get("host") != self._settings.authority:
            raise BoundaryRejected(
                "authority",
                "Request host does not match the installed local origin",
            )

    def _validate_client(self, request: Request) -> None:
        client = request.client
        if client is None or not self._is_loopback(client.host):
            raise BoundaryRejected("client", "The companion accepts loopback clients only")

    def _validate_browser_context(self, request: Request) -> None:
        observation = self._observe_browser_context(request)
        if observation.is_allowed():
            return
        raise BoundaryRejected(
            observation.safe_reason(),
            "Request browser context does not match the installed task pane",
        )

    def _observe_browser_context(self, request: Request) -> BrowserContextObservation:
        headers = request.headers
        return BrowserContextObservation(
            origin=classify_origin(headers.get("origin"), self._settings.origin),
            fetch_site=classify_known(headers.get("sec-fetch-site"), KNOWN_FETCH_SITES),
            fetch_mode=classify_known(headers.get("sec-fetch-mode"), KNOWN_FETCH_MODES),
            fetch_destination=classify_known(
                headers.get("sec-fetch-dest"), KNOWN_FETCH_DESTINATIONS
            ),
        )

    def _is_loopback(self, host: str) -> bool:
        try:
            return ipaddress.ip_address(host).is_loopback
        except ValueError:
            return False


def classify_origin(value: str | None, expected: str) -> str:
    if value is None:
        return "missing"
    if value == expected:
        return "exact"
    if value == "null":
        return "null"
    return "unexpected"


def classify_known(value: str | None, known_values: set[str]) -> str:
    if value is None:
        return "missing"
    return value if value in known_values else "unexpected"
