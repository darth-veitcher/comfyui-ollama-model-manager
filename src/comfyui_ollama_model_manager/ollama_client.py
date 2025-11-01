"""Async HTTP client for Ollama API interactions."""

from typing import Any, Dict, List

import httpx

from .log_config import get_logger

log = get_logger()


async def fetch_models_from_ollama(endpoint: str) -> List[str]:
    """
    Fetch available models from Ollama /api/tags endpoint.

    Args:
        endpoint: Base URL for Ollama API (e.g., http://localhost:11434)

    Returns:
        List of model names available on the Ollama instance

    Raises:
        httpx.HTTPError: If the request fails
    """
    base = endpoint.rstrip("/")
    url = f"{base}/api/tags"

    log.info(f"🔍 Fetching models from {url}")

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()

        # API shape: {"models": [{"name": "llama3.2"}, ...]}
        names = [m["name"] for m in data.get("models", [])]

        log.info(f"✅ Found {len(names)} models")
        log.debug(f"Models: {names}")

        return names

    except httpx.HTTPError as e:
        log.error(f"❌ Failed to fetch models from {url}: {e}")
        raise


async def load_model(
    endpoint: str, model: str, keep_alive: str = "-1"
) -> Dict[str, Any]:
    """
    Load a model into Ollama's memory.

    Try /api/load first (if present), then /api/generate as fallback.

    Args:
        endpoint: Base URL for Ollama API
        model: Name of the model to load
        keep_alive: Time to keep model in memory (-1 = indefinite)

    Returns:
        Response data from Ollama API

    Raises:
        httpx.HTTPError: If the request fails
    """
    base = endpoint.rstrip("/")
    payload: Dict[str, Any] = {"model": model}
    if keep_alive:
        payload["keep_alive"] = keep_alive

    log.info(f"⬇️  Loading model '{model}' (keep_alive={keep_alive})")

    async with httpx.AsyncClient(timeout=60.0) as client:
        # Best-effort /api/load
        try:
            url = f"{base}/api/load"
            log.debug(f"Trying {url}")
            r = await client.post(url, json=payload)
            if r.status_code < 400:
                log.info(f"✅ Model '{model}' loaded successfully via /api/load")
                return r.json()
        except httpx.HTTPError as e:
            log.debug(f"/api/load not available or failed: {e}")

        # Fallback /api/generate (requires prompt field)
        url = f"{base}/api/generate"
        log.debug(f"Falling back to {url}")

        try:
            # /api/generate requires a prompt, use empty string to just load model
            generate_payload = {
                "model": model,
                "prompt": "",
                "keep_alive": keep_alive,
            }
            r = await client.post(url, json=generate_payload)
            r.raise_for_status()
            log.info(f"✅ Model '{model}' loaded successfully via /api/generate")
            return r.json()
        except httpx.HTTPError as e:
            log.error(f"❌ Failed to load model '{model}': {e}")
            raise


async def unload_model(endpoint: str, model: str) -> Dict[str, Any]:
    """
    Unload a model from Ollama's memory.

    Documented unload: call /api/generate with keep_alive = 0.

    Args:
        endpoint: Base URL for Ollama API
        model: Name of the model to unload

    Returns:
        Response data from Ollama API

    Raises:
        httpx.HTTPError: If the request fails
    """
    base = endpoint.rstrip("/")
    url = f"{base}/api/generate"

    log.info(f"⬆️  Unloading model '{model}'")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(
                url,
                json={"model": model, "keep_alive": 0},
            )
            r.raise_for_status()
            log.info(f"✅ Model '{model}' unloaded successfully")
            return r.json()

    except httpx.HTTPError as e:
        log.error(f"❌ Failed to unload model '{model}': {e}")
        raise
