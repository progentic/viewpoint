from dataclasses import replace

import pytest

from researcher_companion.api.bootstrap_policy import (
    BootstrapClassification,
    BootstrapRequestContext,
    BootstrapRequestPolicy,
    word_macos_wkwebview_profile,
)
from researcher_companion.api.errors import BootstrapRejected

EXPECTED_HOST = "localhost:4179"
EXPECTED_ORIGIN = "https://localhost:4179"
POLICY = BootstrapRequestPolicy(word_macos_wkwebview_profile(EXPECTED_HOST, EXPECTED_ORIGIN))


def test_exact_origin_is_authorized() -> None:
    authorization = POLICY.authorize(valid_context())

    assert authorization.classification is BootstrapClassification.EXACT_ORIGIN


def test_missing_origin_verified_profile_is_authorized() -> None:
    context = replace(valid_context(), origin_values=())

    authorization = POLICY.authorize(context)

    assert authorization.classification is BootstrapClassification.MISSING_ORIGIN_VERIFIED_PROFILE


@pytest.mark.parametrize(
    "origins",
    [
        ("https://attacker.example",),
        ("null",),
        (EXPECTED_ORIGIN, EXPECTED_ORIGIN),
        ("http://localhost:4179",),
        ("https://localhost:4180",),
        ("https://127.0.0.1:4179",),
        (f"{EXPECTED_ORIGIN} https://attacker.example",),
        ("not an origin",),
    ],
)
def test_present_nonexact_origin_is_rejected(origins: tuple[str, ...]) -> None:
    decision = POLICY.classify(replace(valid_context(), origin_values=origins))

    assert decision.classification is BootstrapClassification.ORIGIN_UNEXPECTED
    assert decision.error_code == "bootstrap_origin_unexpected"


@pytest.mark.parametrize(
    ("changes", "error_code"),
    [
        ({"host_values": ("localhost:4180",)}, "bootstrap_host_invalid"),
        ({"host_values": ("127.0.0.1:4179",)}, "bootstrap_host_invalid"),
        ({"host_values": ()}, "bootstrap_host_invalid"),
        ({"is_loopback_peer": False}, "bootstrap_peer_not_loopback"),
        ({"scheme": "http"}, "bootstrap_profile_not_allowed"),
        ({"method": "GET"}, "bootstrap_method_invalid"),
        ({"path": "/api/v1/health"}, "bootstrap_path_invalid"),
        ({"content_type_values": ("text/plain",)}, "bootstrap_content_type_invalid"),
        ({"content_type_values": ()}, "bootstrap_content_type_invalid"),
        ({"fetch_site_values": ()}, "bootstrap_fetch_metadata_invalid"),
        ({"fetch_site_values": ("none",)}, "bootstrap_fetch_metadata_invalid"),
        ({"fetch_site_values": ("cross-site",)}, "bootstrap_fetch_metadata_invalid"),
        ({"fetch_mode_values": ()}, "bootstrap_fetch_metadata_invalid"),
        ({"fetch_mode_values": ("navigate",)}, "bootstrap_fetch_metadata_invalid"),
        ({"fetch_destination_values": ()}, "bootstrap_fetch_metadata_invalid"),
        ({"fetch_destination_values": ("document",)}, "bootstrap_fetch_metadata_invalid"),
    ],
)
def test_profile_mismatch_is_rejected(changes: dict[str, object], error_code: str) -> None:
    context = replace(valid_context(), origin_values=(), **changes)

    decision = POLICY.classify(context)

    assert decision.classification is BootstrapClassification.PROFILE_MISMATCH
    assert decision.error_code == error_code
    with pytest.raises(BootstrapRejected) as rejection:
        POLICY.authorize(context)
    assert rejection.value.code == error_code


def test_exact_origin_still_requires_remaining_controls() -> None:
    context = replace(valid_context(), fetch_mode_values=("navigate",))

    decision = POLICY.classify(context)

    assert decision.classification is BootstrapClassification.EXACT_ORIGIN
    assert decision.error_code == "bootstrap_fetch_metadata_invalid"


def valid_context() -> BootstrapRequestContext:
    return BootstrapRequestContext(
        host_values=(EXPECTED_HOST,),
        origin_values=(EXPECTED_ORIGIN,),
        is_loopback_peer=True,
        scheme="https",
        method="POST",
        path="/api/v1/session/bootstrap",
        content_type_values=("application/json",),
        fetch_site_values=("same-origin",),
        fetch_mode_values=("cors",),
        fetch_destination_values=("empty",),
    )
