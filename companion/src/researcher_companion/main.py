import uvicorn

from researcher_companion.api.app import create_app
from researcher_companion.infrastructure.port import StablePortGuard
from researcher_companion.logging_config import configure_safe_logging
from researcher_companion.platform.credentials import (
    InstallationSecretService,
    current_credential_store,
)
from researcher_companion.platform.paths import load_companion_settings
from researcher_companion.settings import CompanionSettings


def main() -> None:
    configure_safe_logging()
    settings = load_companion_settings()
    StablePortGuard().require_available(settings.loopback)
    application = create_runtime_app(settings)
    uvicorn.Server(create_server_config(settings, application)).run()


def create_runtime_app(settings: CompanionSettings):
    secret = InstallationSecretService(current_credential_store()).load()
    return create_app(settings, secret)


def create_server_config(settings: CompanionSettings, application) -> uvicorn.Config:
    settings.validate()
    return uvicorn.Config(
        application,
        host=settings.loopback.bind_host,
        port=settings.loopback.port,
        ssl_certfile=str(settings.paths.certificate),
        ssl_keyfile=str(settings.paths.private_key),
        access_log=False,
        proxy_headers=False,
        server_header=False,
    )


if __name__ == "__main__":
    main()
