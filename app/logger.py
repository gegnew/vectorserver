import logging
import sys

from .settings import settings


def setup_logger(
    name: str = "vectordb",
    level: str | None = None,
    format_string: str | None = None,
) -> logging.Logger:
    """Configure and return a logger with specified name, level, and format."""
    logger = logging.getLogger(name)

    log_level = level or ("DEBUG" if settings.debug else "INFO")
    logger.setLevel(getattr(logging, log_level))

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    handler = logging.StreamHandler(sys.stdout)

    default_format = (
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        if not settings.debug
        else "%(asctime)s - %(name)s - %(levelname)s -\
        %(funcName)s:%(lineno)d - %(message)s"
    )

    formatter = logging.Formatter(format_string or default_format)
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


logger = setup_logger()
