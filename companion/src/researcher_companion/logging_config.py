import logging

SAFE_LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s event=%(message)s"


def configure_safe_logging() -> None:
    logging.basicConfig(level=logging.INFO, format=SAFE_LOG_FORMAT)
