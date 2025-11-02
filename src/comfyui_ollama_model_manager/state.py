"""Global state management for Ollama models cache."""

import threading
from typing import Dict, List

from .log_config import get_logger

log = get_logger()

# Default endpoint; can be overridden by the refresh node
_OLLAMA_ENDPOINT = "http://localhost:11434"

# Per-endpoint model cache
_MODELS_CACHE: Dict[str, List[str]] = {}

# Legacy: List of model names from /api/tags (for backwards compatibility)
_OLLAMA_MODELS: List[str] = []

# Avoid concurrent updates
_OLLAMA_LOCK = threading.Lock()


def set_models(endpoint: str, names: List[str]) -> None:
    """Store models in the global cache (both per-endpoint and legacy)."""
    global _OLLAMA_ENDPOINT, _OLLAMA_MODELS, _MODELS_CACHE
    with _OLLAMA_LOCK:
        _OLLAMA_ENDPOINT = endpoint
        _OLLAMA_MODELS = names  # Legacy support
        _MODELS_CACHE[endpoint] = names  # Per-endpoint cache
        log.info(f"📋 Updated model cache with {len(names)} models from {endpoint}")
        log.debug(f"Models: {names}")


def get_models(endpoint: str | None = None) -> List[str]:
    """
    Return cached model names for the given endpoint.
    If endpoint is None, returns legacy global cache.
    Returns empty list if endpoint not found in cache.
    """
    with _OLLAMA_LOCK:
        if endpoint is None:
            # Legacy behavior
            return list(_OLLAMA_MODELS)
        else:
            # Per-endpoint cache
            return list(_MODELS_CACHE.get(endpoint, []))


def get_endpoint() -> str:
    """Return the current Ollama endpoint."""
    with _OLLAMA_LOCK:
        return _OLLAMA_ENDPOINT
