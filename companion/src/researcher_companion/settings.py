from dataclasses import dataclass
from pathlib import Path

STABLE_HOSTNAME = "localhost"
STABLE_PORT = 4179
LOOPBACK_ADDRESS = "127.0.0.1"


@dataclass(frozen=True)
class LoopbackSettings:
    bind_host: str = LOOPBACK_ADDRESS
    hostname: str = STABLE_HOSTNAME
    port: int = STABLE_PORT

    @property
    def origin(self) -> str:
        return f"https://{self.hostname}:{self.port}"

    @property
    def authority(self) -> str:
        return f"{self.hostname}:{self.port}"

    def require_loopback(self) -> None:
        if self.bind_host != LOOPBACK_ADDRESS:
            raise ValueError("Companion bind address must be IPv4 loopback")


@dataclass(frozen=True)
class SessionSettings:
    bootstrap_ttl_seconds: int = 30
    session_ttl_seconds: int = 900


@dataclass(frozen=True)
class RuntimePaths:
    database: Path
    content_store: Path
    taskpane_index: Path
    taskpane_assets: Path
    certificate: Path
    private_key: Path
    migrations: Path


@dataclass(frozen=True)
class CompanionSettings:
    loopback: LoopbackSettings
    session: SessionSettings
    paths: RuntimePaths

    def validate(self) -> None:
        self.loopback.require_loopback()
