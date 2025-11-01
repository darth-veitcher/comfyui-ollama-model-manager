"""ComfyUI node definitions for Ollama model management."""

import json
import uuid
from typing import Optional, Tuple

from .async_utils import run_async
from .log_config import get_logger, set_request_id
from .ollama_client import fetch_models_from_ollama, load_model, unload_model
from .state import get_endpoint, get_models, set_models

log = get_logger()


class OllamaRefreshModelList:
    """
    Call Ollama /api/tags and update the module-level cache.
    Then other nodes (select/load/unload) can show those models as dropdowns.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "endpoint": (
                    "STRING",
                    {
                        "default": get_endpoint(),
                        "multiline": False,
                    },
                ),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("models_json",)
    FUNCTION = "run"
    CATEGORY = "Ollama"

    def run(self, endpoint: str) -> Tuple[str]:
        """Refresh the list of available models from Ollama."""
        # Set correlation ID for this operation
        request_id = str(uuid.uuid4())[:8]
        set_request_id(f"refresh-{request_id}")

        log.info(f"🔄 Refreshing model list from {endpoint}")

        try:
            names = run_async(fetch_models_from_ollama(endpoint))

            if not names:
                log.warning("⚠️  No models returned from Ollama")
                names = ["<no-models-returned>"]

            set_models(endpoint, names)
            result = json.dumps(names, indent=2)

            log.info(f"✅ Model list refreshed: {len(names)} models available")
            return (result,)

        except Exception as e:
            log.exception(f"💥 Failed to refresh model list: {e}")
            raise


class OllamaSelectModel:
    """
    Select a model either by typing its name or from the refreshed list.

    If models_json is provided (connected from OllamaRefreshModelList), it will
    parse the JSON and offer those models as options. Otherwise, uses cached models
    or allows manual string entry.
    """

    @classmethod
    def INPUT_TYPES(cls):
        models = get_models()
        if not models:
            models = []

        return {
            "required": {
                "model": (
                    "STRING",
                    {
                        "default": models[0] if models else "",
                        "multiline": False,
                    },
                ),
            },
            "optional": {
                "models_json": ("STRING", {"forceInput": True}),
            },
        }

    @classmethod
    def IS_CHANGED(cls, model, models_json=None):
        """Force UI to re-query INPUT_TYPES when models cache changes."""
        models = get_models()
        return str(hash(tuple(models)))

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("model",)
    FUNCTION = "run"
    CATEGORY = "Ollama"

    def run(self, model: str, models_json: Optional[str] = None) -> Tuple[str]:
        """Select a model from the cached list or use provided model name."""
        request_id = str(uuid.uuid4())[:8]
        set_request_id(f"select-{request_id}")

        # If models_json is provided, update the cache
        if models_json:
            try:
                models = json.loads(models_json)
                if isinstance(models, list):
                    # Update global cache so other nodes can use it
                    endpoint = get_endpoint()
                    set_models(endpoint, models)
                    log.debug(
                        f"Updated model cache from connected input: {len(models)} models"
                    )
            except json.JSONDecodeError:
                log.warning(f"Failed to parse models_json: {models_json}")

        log.info(f"🎯 Selected model: '{model}'")

        # Just echo the selection forward
        return (model,)


class OllamaLoadSelectedModel:
    """
    Loads a model into Ollama's memory.

    Accepts model name as string (manual entry or from OllamaSelectModel).
    If Ollama doesn't have the model, it will attempt to pull it automatically.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "endpoint": (
                    "STRING",
                    {
                        "default": get_endpoint(),
                        "multiline": False,
                    },
                ),
                "model": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": False,
                    },
                ),
                "keep_alive": (
                    "STRING",
                    {
                        "default": "-1",
                        "multiline": False,
                    },
                ),
            },
            "optional": {
                "models_json": ("STRING", {"forceInput": True}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)
    FUNCTION = "run"
    CATEGORY = "Ollama"

    def run(
        self,
        endpoint: str,
        model: str,
        keep_alive: str,
        models_json: Optional[str] = None,
    ) -> Tuple[str]:
        """Load the selected model into Ollama's memory."""
        request_id = str(uuid.uuid4())[:8]
        set_request_id(f"load-{request_id}")

        # If models_json is provided, update the cache
        if models_json:
            try:
                models = json.loads(models_json)
                if isinstance(models, list):
                    set_models(endpoint, models)
                    log.debug(
                        f"Updated model cache from connected input: {len(models)} models"
                    )
            except json.JSONDecodeError:
                log.warning(f"Failed to parse models_json: {models_json}")

        log.info(f"🚀 Loading model '{model}' from {endpoint}")

        try:
            data = run_async(load_model(endpoint, model, keep_alive))
            result = json.dumps(data, indent=2)

            log.info(f"✅ Model '{model}' loaded successfully")
            return (result,)

        except Exception as e:
            log.exception(f"💥 Failed to load model '{model}': {e}")
            raise


class OllamaUnloadSelectedModel:
    """
    Unloads a model from Ollama's memory (keep_alive=0).

    Accepts model name as string (manual entry or from OllamaSelectModel).
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "endpoint": (
                    "STRING",
                    {
                        "default": get_endpoint(),
                        "multiline": False,
                    },
                ),
                "model": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": False,
                    },
                ),
            },
            "optional": {
                "models_json": ("STRING", {"forceInput": True}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)
    FUNCTION = "run"
    CATEGORY = "Ollama"

    def run(
        self, endpoint: str, model: str, models_json: Optional[str] = None
    ) -> Tuple[str]:
        """Unload the selected model from Ollama's memory."""
        request_id = str(uuid.uuid4())[:8]
        set_request_id(f"unload-{request_id}")

        # If models_json is provided, update the cache
        if models_json:
            try:
                models = json.loads(models_json)
                if isinstance(models, list):
                    set_models(endpoint, models)
                    log.debug(
                        f"Updated model cache from connected input: {len(models)} models"
                    )
            except json.JSONDecodeError:
                log.warning(f"Failed to parse models_json: {models_json}")

        log.info(f"🗑️  Unloading model '{model}' from {endpoint}")

        try:
            data = run_async(unload_model(endpoint, model))
            result = json.dumps(data, indent=2)

            log.info(f"✅ Model '{model}' unloaded successfully")
            return (result,)

        except Exception as e:
            log.exception(f"💥 Failed to unload model '{model}': {e}")
            raise
