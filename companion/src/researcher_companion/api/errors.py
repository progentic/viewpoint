class SessionRejected(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class BoundaryRejected(Exception):
    def __init__(self, reason: str, message: str) -> None:
        super().__init__(message)
        self.reason = reason


BOOTSTRAP_ERROR_MESSAGES = {
    "bootstrap_origin_unexpected": "The request origin is not allowed",
    "bootstrap_profile_not_allowed": "The embedded-host profile is not allowed",
    "bootstrap_host_invalid": "The request host is not allowed",
    "bootstrap_peer_not_loopback": "The request client is not local",
    "bootstrap_fetch_metadata_invalid": "The browser request context is not allowed",
    "bootstrap_method_invalid": "The bootstrap method is not allowed",
    "bootstrap_path_invalid": "The bootstrap path is not allowed",
    "bootstrap_content_type_invalid": "The bootstrap content type is not allowed",
    "bootstrap_replay_rejected": "Reload the task pane to renew local access",
    "bootstrap_session_failed": "The local session could not be created",
}


class BootstrapRejected(Exception):
    def __init__(self, code: str) -> None:
        fallback = BOOTSTRAP_ERROR_MESSAGES["bootstrap_session_failed"]
        message = BOOTSTRAP_ERROR_MESSAGES.get(code, fallback)
        super().__init__(message)
        self.code = code
