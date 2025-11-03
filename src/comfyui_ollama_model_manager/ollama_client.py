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
        keep_alive: Time to keep model in memory (e.g., "5m", "1h", "0", or "-1" for indefinite)

    Returns:
        Response data from Ollama API

    Raises:
        httpx.HTTPError: If the request fails
        ValueError: If model name is empty
    """
    if not model or not model.strip():
        raise ValueError("Model name cannot be empty")

    base = endpoint.rstrip("/")

    # Convert -1 to a valid duration string for /api/generate
    # /api/load accepts -1, but /api/generate needs proper duration format
    # Use a very long duration (999 years) to simulate "indefinite"
    keep_alive_for_generate = "8760000h" if keep_alive == "-1" else keep_alive

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

        # Fallback /api/generate (requires prompt field, returns streaming response)
        url = f"{base}/api/generate"
        log.debug(f"Falling back to {url}")

        try:
            # /api/generate requires a prompt, use empty string to just load model
            # Set stream=false to get a single JSON response instead of streaming
            generate_payload = {
                "model": model,
                "prompt": "",
                "stream": False,
                "keep_alive": keep_alive_for_generate,
            }
            r = await client.post(url, json=generate_payload)

            # Log response details if there's an error
            if r.status_code >= 400:
                log.error(f"Ollama API error response: {r.text}")

            r.raise_for_status()
            log.info(f"✅ Model '{model}' loaded successfully via /api/generate")
            return r.json()
        except httpx.HTTPStatusError as e:
            log.error(f"❌ Failed to load model '{model}': {e}")
            # Try to get more details from response
            try:
                error_detail = e.response.text
                log.error(f"Error details: {error_detail}")
            except Exception:
                pass
            raise
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


async def chat_completion(
    endpoint: str,
    model: str,
    messages: List[Dict[str, Any]],
    options: Dict[str, Any] | None = None,
    images: List[str] | None = None,
    format: str | None = None,
) -> Dict[str, Any]:
    """
    Generate chat completion using Ollama's /api/chat endpoint.

    This function uses Ollama's OpenAI-compatible chat API to generate
    responses based on conversation history.

    Args:
        endpoint: Base URL for Ollama API (e.g., http://localhost:11434)
        model: Name of the model to use for generation
        messages: List of message dicts with 'role' and 'content' keys
                  Example: [{"role": "user", "content": "Hello"}]
        options: Optional dict of generation parameters:
                 - temperature (float): Controls randomness (0.0-2.0)
                 - seed (int): Random seed for reproducibility
                 - num_predict (int): Max tokens to generate
                 - top_p (float): Nucleus sampling (0.0-1.0)
                 - top_k (int): Top-k sampling
                 - repeat_penalty (float): Penalty for repetition
                 - num_ctx (int): Context window size
                 - And other Ollama-specific parameters
        images: Optional list of base64-encoded images for vision models
        format: Optional format for structured output:
                - "json": Force model to respond with valid JSON
                - None: Free-form text response (default)

    Returns:
        Response dict with structure:
        {
            "model": "llama3.2",
            "message": {
                "role": "assistant",
                "content": "Response text here"
            },
            "done": true,
            ...additional metadata...
        }

    Raises:
        httpx.HTTPError: If the request fails
        ValueError: If model or messages are invalid

    Example:
        >>> messages = [
        ...     {"role": "system", "content": "You are helpful."},
        ...     {"role": "user", "content": "Hello!"}
        ... ]
        >>> result = await chat_completion(
        ...     "http://localhost:11434",
        ...     "llama3.2",
        ...     messages,
        ...     options={"temperature": 0.7, "seed": 42}
        ... )
        >>> print(result["message"]["content"])

        >>> # JSON mode example
        >>> result = await chat_completion(
        ...     "http://localhost:11434",
        ...     "llama3.2",
        ...     messages=[{"role": "user", "content": "List 3 colors"}],
        ...     format="json"
        ... )
        >>> import json
        >>> data = json.loads(result["message"]["content"])
    """
    if not model or not model.strip():
        raise ValueError("Model name cannot be empty")

    if not messages or not isinstance(messages, list):
        raise ValueError("Messages must be a non-empty list")

    base = endpoint.rstrip("/")
    url = f"{base}/api/chat"

    # Build request payload
    payload: Dict[str, Any] = {
        "model": model,
        "messages": messages,
        "stream": False,  # We want a single response, not streaming
    }

    # Add optional parameters
    if options:
        payload["options"] = options

    if format:
        payload["format"] = format
        log.debug(f"Using format: {format}")

    if images:
        # Add images to the last user message
        # This follows Ollama's vision API format
        if messages and messages[-1].get("role") == "user":
            messages[-1]["images"] = images

    log.info(f"💬 Chat completion with model '{model}' ({len(messages)} messages)")
    log.debug(f"Messages: {messages}")
    if options:
        log.debug(f"Options: {options}")

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            r = await client.post(url, json=payload)

            # Log error details if request fails
            if r.status_code >= 400:
                log.error(f"Ollama API error response: {r.text}")

            r.raise_for_status()
            result = r.json()

            # Extract response content for logging
            response_content = result.get("message", {}).get("content", "")
            log.info(f"✅ Generated {len(response_content)} characters")
            log.debug(f"Response: {response_content[:100]}...")

            return result

    except httpx.HTTPStatusError as e:
        log.error(f"❌ Chat completion failed: {e}")
        try:
            error_detail = e.response.text
            log.error(f"Error details: {error_detail}")
        except Exception:
            pass
        raise
    except httpx.HTTPError as e:
        log.error(f"❌ Chat completion failed: {e}")
        raise
