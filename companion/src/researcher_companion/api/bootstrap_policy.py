from dataclasses import dataclass
from enum import StrEnum

from researcher_companion.api.errors import BootstrapRejected


class BootstrapClassification(StrEnum):
    EXACT_ORIGIN = "exact_origin"
    MISSING_ORIGIN_VERIFIED_PROFILE = "missing_origin_verified_profile"
    ORIGIN_UNEXPECTED = "origin_unexpected"
    PROFILE_MISMATCH = "profile_mismatch"


@dataclass(frozen=True)
class BootstrapRequestContext:
    host_values: tuple[str, ...]
    origin_values: tuple[str, ...]
    is_loopback_peer: bool
    scheme: str
    method: str
    path: str
    content_type_values: tuple[str, ...]
    fetch_site_values: tuple[str, ...]
    fetch_mode_values: tuple[str, ...]
    fetch_destination_values: tuple[str, ...]


@dataclass(frozen=True)
class EmbeddedHostProfile:
    profile_id: str
    host: str
    origin: str
    scheme: str
    method: str
    path: str
    content_type: str
    fetch_site: str
    fetch_mode: str
    fetch_destination: str


@dataclass(frozen=True)
class AuthorizedBootstrapRequest:
    classification: BootstrapClassification
    profile_id: str


@dataclass(frozen=True)
class BootstrapPolicyDecision:
    classification: BootstrapClassification
    profile_id: str
    error_code: str | None = None

    @property
    def is_allowed(self) -> bool:
        return self.error_code is None


class BootstrapRequestPolicy:
    def __init__(self, profile: EmbeddedHostProfile) -> None:
        self._profile = profile

    def authorize(self, context: BootstrapRequestContext) -> AuthorizedBootstrapRequest:
        decision = self.classify(context)
        if not decision.is_allowed:
            raise BootstrapRejected(decision.error_code or "bootstrap_profile_not_allowed")
        return AuthorizedBootstrapRequest(decision.classification, decision.profile_id)

    def classify(self, context: BootstrapRequestContext) -> BootstrapPolicyDecision:
        origin_classification = self._classify_origin(context.origin_values)
        if origin_classification is BootstrapClassification.ORIGIN_UNEXPECTED:
            return self._reject(origin_classification, "bootstrap_origin_unexpected")
        mismatch = self._profile_mismatch(context)
        if mismatch is not None:
            classification = self._mismatch_classification(origin_classification)
            return self._reject(classification, mismatch)
        return self._accept(origin_classification)

    def _classify_origin(self, values: tuple[str, ...]) -> BootstrapClassification:
        if not values:
            return BootstrapClassification.MISSING_ORIGIN_VERIFIED_PROFILE
        if values == (self._profile.origin,):
            return BootstrapClassification.EXACT_ORIGIN
        return BootstrapClassification.ORIGIN_UNEXPECTED

    def _profile_mismatch(self, context: BootstrapRequestContext) -> str | None:
        checks = (
            self._host_error(context),
            self._peer_error(context),
            self._scheme_error(context),
            self._method_error(context),
            self._path_error(context),
            self._content_type_error(context),
            self._fetch_metadata_error(context),
        )
        return next((error for error in checks if error is not None), None)

    def _host_error(self, context: BootstrapRequestContext) -> str | None:
        return self._exact_error(
            context.host_values,
            self._profile.host,
            "bootstrap_host_invalid",
        )

    def _peer_error(self, context: BootstrapRequestContext) -> str | None:
        return None if context.is_loopback_peer else "bootstrap_peer_not_loopback"

    def _scheme_error(self, context: BootstrapRequestContext) -> str | None:
        return None if context.scheme == self._profile.scheme else "bootstrap_profile_not_allowed"

    def _method_error(self, context: BootstrapRequestContext) -> str | None:
        return None if context.method == self._profile.method else "bootstrap_method_invalid"

    def _path_error(self, context: BootstrapRequestContext) -> str | None:
        return None if context.path == self._profile.path else "bootstrap_path_invalid"

    def _content_type_error(self, context: BootstrapRequestContext) -> str | None:
        return self._exact_error(
            context.content_type_values,
            self._profile.content_type,
            "bootstrap_content_type_invalid",
        )

    def _fetch_metadata_error(self, context: BootstrapRequestContext) -> str | None:
        expected = (
            (context.fetch_site_values, self._profile.fetch_site),
            (context.fetch_mode_values, self._profile.fetch_mode),
            (context.fetch_destination_values, self._profile.fetch_destination),
        )
        matches = all(values == (value,) for values, value in expected)
        return None if matches else "bootstrap_fetch_metadata_invalid"

    def _exact_error(
        self,
        values: tuple[str, ...],
        expected: str,
        error_code: str,
    ) -> str | None:
        return None if values == (expected,) else error_code

    def _mismatch_classification(
        self,
        origin_classification: BootstrapClassification,
    ) -> BootstrapClassification:
        if origin_classification is BootstrapClassification.EXACT_ORIGIN:
            return origin_classification
        return BootstrapClassification.PROFILE_MISMATCH

    def _accept(
        self,
        classification: BootstrapClassification,
    ) -> BootstrapPolicyDecision:
        return BootstrapPolicyDecision(classification, self._profile.profile_id)

    def _reject(
        self,
        classification: BootstrapClassification,
        error_code: str,
    ) -> BootstrapPolicyDecision:
        return BootstrapPolicyDecision(classification, self._profile.profile_id, error_code)


def word_macos_wkwebview_profile(host: str, origin: str) -> EmbeddedHostProfile:
    return EmbeddedHostProfile(
        profile_id="word-macos-wkwebview",
        host=host,
        origin=origin,
        scheme="https",
        method="POST",
        path="/api/v1/session/bootstrap",
        content_type="application/json",
        fetch_site="same-origin",
        fetch_mode="cors",
        fetch_destination="empty",
    )
