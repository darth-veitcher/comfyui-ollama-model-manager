"""Global state management for Ollama models cache."""

import threading
from typing import List

from .log_config import get_logger

log = get_logger()

# Default endpoint; can be overridden by the refresh node
_OLLAMA_ENDPOINT = "http://localhost:11434"

# List of model names from /api/tags
_OLLAMA_MODELS: List[str] = []

# Avoid concurrent updates
_OLLAMA_LOCK = threading.Lock()


def set_models(endpoint: str, names: List[str]) -> None:
    """Store models in the global cache."""
    global _OLLAMA_ENDPOINT, _OLLAMA_MODELS
    with _OLLAMA_LOCK:
        _OLLAMA_ENDPOINT = endpoint
        _OLLAMA_MODELS = names
        log.info(f"📋 Updated model cache with {len(names)} models from {endpoint}")
        log.debug(f"Models: {names}")


def get_models() -> List[str]:
    """Return cached model names (may be empty)."""
    with _OLLAMA_LOCK:
        return list(_OLLAMA_MODELS)


def get_endpoint() -> str:
    """Return the current Ollama endpoint."""
    with _OLLAMA_LOCK:
        return _OLLAMA_ENDPOINT
