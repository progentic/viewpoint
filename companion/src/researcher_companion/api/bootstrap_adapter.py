import ipaddress

from fastapi import Request

from researcher_companion.api.bootstrap_policy import BootstrapRequestContext


def extract_bootstrap_context(request: Request) -> BootstrapRequestContext:
    return BootstrapRequestContext(
        host_values=header_values(request, "host"),
        origin_values=header_values(request, "origin"),
        is_loopback_peer=is_loopback_client(request),
        scheme=str(request.scope.get("scheme", "")),
        method=str(request.scope.get("method", "")),
        path=str(request.scope.get("path", "")),
        content_type_values=header_values(request, "content-type"),
        fetch_site_values=header_values(request, "sec-fetch-site"),
        fetch_mode_values=header_values(request, "sec-fetch-mode"),
        fetch_destination_values=header_values(request, "sec-fetch-dest"),
    )


def header_values(request: Request, name: str) -> tuple[str, ...]:
    return tuple(request.headers.getlist(name))


def is_loopback_client(request: Request) -> bool:
    client = request.client
    return client is not None and is_loopback_address(client.host)


def is_loopback_address(value: str) -> bool:
    try:
        return ipaddress.ip_address(value).is_loopback
    except ValueError:
        return False
