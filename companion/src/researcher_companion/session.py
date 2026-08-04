import base64
import hashlib
import hmac
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta

from researcher_companion.api.errors import SessionRejected
from researcher_companion.clock import Clock
from researcher_companion.settings import SessionSettings

BOOTSTRAP_COOKIE = "wr_bootstrap"
SESSION_COOKIE = "wr_session"


@dataclass(frozen=True)
class BootstrapMaterial:
    cookie: str
    csrf_token: str
    expires_at: datetime


@dataclass(frozen=True)
class SessionMaterial:
    cookie: str
    csrf_token: str
    expires_at: datetime


@dataclass(frozen=True)
class PendingBootstrap:
    csrf_digest: bytes
    expires_at: datetime


@dataclass(frozen=True)
class ActiveSession:
    csrf_digest: bytes
    expires_at: datetime


class LocalSessionManager:
    def __init__(self, secret: bytes, settings: SessionSettings, clock: Clock) -> None:
        if len(secret) < 32:
            raise ValueError("Installation secret must contain at least 32 bytes")
        self._secret = secret
        self._settings = settings
        self._clock = clock
        self._pending: dict[str, PendingBootstrap] = {}
        self._sessions: dict[bytes, ActiveSession] = {}

    def issue_bootstrap(self) -> BootstrapMaterial:
        challenge_id = secrets.token_urlsafe(24)
        csrf_token = secrets.token_urlsafe(24)
        expires_at = self._expiry(self._settings.bootstrap_ttl_seconds)
        self._pending[challenge_id] = PendingBootstrap(self._digest(csrf_token), expires_at)
        cookie = self._encode_challenge(challenge_id, expires_at)
        return BootstrapMaterial(cookie, csrf_token, expires_at)

    def establish(
        self,
        challenge_cookie: str | None,
        csrf_token: str | None,
        previous_session_cookie: str | None = None,
    ) -> SessionMaterial:
        challenge_id = self._validate_challenge(challenge_cookie)
        self._consume_pending(challenge_id, csrf_token)
        self._remove_session(previous_session_cookie)
        return self._issue_session()

    def validate(self, session_cookie: str | None, csrf_token: str | None) -> None:
        if not session_cookie:
            raise SessionRejected(
                "missing_session", "Open the task pane to establish a local session"
            )
        session = self._sessions.get(self._digest(session_cookie))
        self._validate_active_session(session_cookie, csrf_token, session)

    def _validate_challenge(self, cookie: str | None) -> str:
        if not cookie:
            raise SessionRejected(
                "missing_bootstrap", "Reload the task pane to start a local session"
            )
        challenge_id, expires_at, signature = self._decode_challenge(cookie)
        expected = self._sign(challenge_id, expires_at)
        if not hmac.compare_digest(signature, expected):
            raise SessionRejected("invalid_bootstrap", "Reload the task pane to renew local access")
        if self._clock.now().timestamp() > expires_at:
            raise SessionRejected("expired_bootstrap", "Reload the task pane to renew local access")
        return challenge_id

    def _consume_pending(self, challenge_id: str, csrf_token: str | None) -> PendingBootstrap:
        pending = self._pending.pop(challenge_id, None)
        if pending is None or csrf_token is None:
            raise SessionRejected("invalid_bootstrap", "Reload the task pane to renew local access")
        if self._clock.now() > pending.expires_at:
            raise SessionRejected("expired_bootstrap", "Reload the task pane to renew local access")
        if not hmac.compare_digest(pending.csrf_digest, self._digest(csrf_token)):
            raise SessionRejected("invalid_bootstrap", "Reload the task pane to renew local access")
        return pending

    def _issue_session(self) -> SessionMaterial:
        cookie = secrets.token_urlsafe(32)
        csrf_token = secrets.token_urlsafe(24)
        expires_at = self._expiry(self._settings.session_ttl_seconds)
        self._sessions[self._digest(cookie)] = ActiveSession(self._digest(csrf_token), expires_at)
        return SessionMaterial(cookie, csrf_token, expires_at)

    def _remove_session(self, session_cookie: str | None) -> None:
        if session_cookie is not None:
            self._sessions.pop(self._digest(session_cookie), None)

    def _validate_active_session(
        self,
        cookie: str,
        csrf_token: str | None,
        session: ActiveSession | None,
    ) -> None:
        if session is None or csrf_token is None:
            raise SessionRejected("invalid_session", "Reload the task pane to renew local access")
        if self._clock.now() > session.expires_at:
            self._sessions.pop(self._digest(cookie), None)
            raise SessionRejected("expired_session", "Reload the task pane to renew local access")
        if not hmac.compare_digest(session.csrf_digest, self._digest(csrf_token)):
            raise SessionRejected("invalid_session", "Reload the task pane to renew local access")

    def _encode_challenge(self, challenge_id: str, expires_at: datetime) -> str:
        expiry = int(expires_at.timestamp())
        payload = f"{challenge_id}.{expiry}.{self._sign(challenge_id, expiry)}"
        return base64.urlsafe_b64encode(payload.encode()).decode().rstrip("=")

    def _decode_challenge(self, cookie: str) -> tuple[str, int, str]:
        try:
            padding = "=" * (-len(cookie) % 4)
            payload = base64.urlsafe_b64decode(cookie + padding).decode()
            challenge_id, expiry, signature = payload.split(".")
            return challenge_id, int(expiry), signature
        except (ValueError, UnicodeDecodeError) as error:
            raise SessionRejected(
                "invalid_bootstrap", "Reload the task pane to renew local access"
            ) from error

    def _sign(self, challenge_id: str, expires_at: int | datetime) -> str:
        expiry = int(expires_at.timestamp()) if isinstance(expires_at, datetime) else expires_at
        message = f"{challenge_id}.{expiry}".encode()
        return hmac.new(self._secret, message, hashlib.sha256).hexdigest()

    def _digest(self, value: str) -> bytes:
        return hmac.new(self._secret, value.encode(), hashlib.sha256).digest()

    def _expiry(self, ttl_seconds: int) -> datetime:
        return self._clock.now() + timedelta(seconds=ttl_seconds)
