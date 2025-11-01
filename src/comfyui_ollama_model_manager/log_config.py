"""Logging configuration for ComfyUI Ollama Model Manager."""

import sys
import logging
import contextvars
import re
from pathlib import Path
from loguru import logger

# Context variable for request correlation
cid = contextvars.ContextVar("cid", default="-")

# Security: Scrub sensitive data from logs
SECRET_PATTERN = re.compile(r"(Bearer\s+[A-Za-z0-9\-_.]{20,})")


def scrub_secrets(text: str) -> str:
    """Remove sensitive tokens from log messages."""
    return SECRET_PATTERN.sub("Bearer <redacted>", text)


def patch_record(record):
    """Enrich log records with context and scrub secrets."""
    record["extra"]["cid"] = cid.get()
    record["message"] = scrub_secrets(record["message"])
    return record


# Bridge stdlib logging to Loguru
class InterceptHandler(logging.Handler):
    """Intercept standard logging and redirect to Loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


# Configure stdlib logging
logging.basicConfig(handlers=[InterceptHandler()], level=logging.NOTSET, force=True)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

# Configure Loguru sinks
logger.remove()

# Console output
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{extra[cid]}</cyan> | <level>{message}</level>",
    level="INFO",
    colorize=True,
)

# JSON file logging for production
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logger.add(
    log_dir / "ollama_manager.json",
    level="DEBUG",
    serialize=True,
    rotation="1 day",
    retention="14 days",
    compression="zip",
    enqueue=True,
)


def set_request_id(request_id: str) -> None:
    """Set the correlation ID for the current context."""
    cid.set(request_id)


def get_logger():
    """Get the configured logger instance."""
    return logger.patch(patch_record)
