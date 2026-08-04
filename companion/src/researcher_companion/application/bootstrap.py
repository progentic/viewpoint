from researcher_companion.api.bootstrap_policy import (
    AuthorizedBootstrapRequest,
    BootstrapRequestContext,
    BootstrapRequestPolicy,
)
from researcher_companion.api.errors import BootstrapRejected, SessionRejected
from researcher_companion.session import LocalSessionManager, SessionMaterial


class BootstrapUseCase:
    def __init__(
        self,
        policy: BootstrapRequestPolicy,
        sessions: LocalSessionManager,
    ) -> None:
        self._policy = policy
        self._sessions = sessions

    def authorize(self, context: BootstrapRequestContext) -> AuthorizedBootstrapRequest:
        return self._policy.authorize(context)

    def establish(
        self,
        authorization: AuthorizedBootstrapRequest,
        challenge_cookie: str | None,
        bootstrap_csrf: str | None,
        previous_session_cookie: str | None,
    ) -> SessionMaterial:
        del authorization
        try:
            return self._sessions.establish(
                challenge_cookie,
                bootstrap_csrf,
                previous_session_cookie,
            )
        except SessionRejected as error:
            raise map_session_rejection(error) from error


def map_session_rejection(error: SessionRejected) -> BootstrapRejected:
    if error.code in BOOTSTRAP_REPLAY_CODES:
        return BootstrapRejected("bootstrap_replay_rejected")
    return BootstrapRejected("bootstrap_session_failed")


BOOTSTRAP_REPLAY_CODES = {
    "missing_bootstrap",
    "invalid_bootstrap",
    "expired_bootstrap",
}
