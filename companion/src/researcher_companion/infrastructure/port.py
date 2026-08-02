import socket

from researcher_companion.settings import LoopbackSettings


class StablePortGuard:
    def require_available(self, settings: LoopbackSettings) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
            try:
                listener.bind((settings.bind_host, settings.port))
            except OSError as error:
                message = (
                    f"Stable loopback port {settings.port} is unavailable; "
                    "stop the owner and repair"
                )
                raise RuntimeError(
                    message
                ) from error
