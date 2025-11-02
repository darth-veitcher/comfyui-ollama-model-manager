"""ComfyUI node definitions for Ollama model management."""

import json
import uuid
from typing import Any, Tuple

from .async_utils import run_async
from .log_config import get_logger, set_request_id
from .ollama_client import fetch_models_from_ollama, load_model, unload_model
from .state import get_endpoint, get_models, set_models

log = get_logger()


class OllamaClient:
    """
    Ollama Client configuration node.
    Specifies the endpoint for Ollama API.
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
            },
        }

    RETURN_TYPES = ("OLLAMA_CLIENT",)
    RETURN_NAMES = ("client",)
    FUNCTION = "create_client"
    CATEGORY = "Ollama"

    def create_client(self, endpoint: str) -> Tuple[dict]:
        """Create an Ollama client configuration."""
        request_id = str(uuid.uuid4())[:8]
        set_request_id(f"client-{request_id}")

        log.info(f"🔌 Created Ollama client for {endpoint}")

        client_config = {
            "endpoint": endpoint,
            "type": "ollama_client",
        }

        return (client_config,)


class OllamaModelSelector:
    """
    Select an Ollama model.
    Automatically refreshes model list when connected to OllamaClient.
    Displays models as a dynamic dropdown.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "client": ("OLLAMA_CLIENT",),
                "model": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": False,
                    },
                ),
            },
            "optional": {
                "refresh": ("BOOLEAN", {"default": False}),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
            },
        }

    RETURN_TYPES = ("OLLAMA_CLIENT", "STRING", "STRING")
    RETURN_NAMES = ("client", "model", "models_json")
    FUNCTION = "select_model"
    CATEGORY = "Ollama"
    OUTPUT_NODE = True

    def select_model(
        self, client: dict, model: str, refresh: bool = False, unique_id=None
    ):
        """Select a model and optionally refresh the list."""
        request_id = str(uuid.uuid4())[:8]
        set_request_id(f"select-{request_id}")

        endpoint = client.get("endpoint", "")
        if not endpoint:
            raise ValueError("Client endpoint not specified")

        # Always get or refresh models
        names = []
        if refresh:
            log.info(f"🔄 Refreshing model list from {endpoint}")
            try:
                names = run_async(fetch_models_from_ollama(endpoint))
                if not names:
                    log.warning("⚠️  No models returned from Ollama")
                    names = ["<no-models-returned>"]
                set_models(endpoint, names)
                log.info(f"✅ Model list refreshed: {len(names)} models available")
            except Exception as e:
                log.exception(f"💥 Failed to refresh model list: {e}")
                # Fall back to cached models
                names = get_models(endpoint)
        else:
            # Get cached models
            names = get_models(endpoint)

        log.info(f"🎯 Selected model: '{model}'")

        # Create JSON output for downstream nodes
        models_json = json.dumps(names)

        # Return with UI data for JavaScript
        return {
            "ui": {
                "models_json": [models_json],
                "model_count": [len(names)],
                "model_list": [names],
            },
            "result": (client, model, models_json),
        }


class OllamaLoadModel:
    """
    Loads a model into Ollama's memory.
    Takes client and model from OllamaClient and OllamaModelSelector.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "client": ("OLLAMA_CLIENT",),
                "model": ("STRING",),
                "keep_alive": (
                    "STRING",
                    {
                        "default": "-1",
                        "multiline": False,
                    },
                ),
            },
            "optional": {
                "dependencies": ("*",),
            },
        }

    RETURN_TYPES = ("OLLAMA_CLIENT", "STRING", "*")
    RETURN_NAMES = ("client", "result", "dependencies")
    FUNCTION = "load_model_op"
    CATEGORY = "Ollama"

    def load_model_op(
        self,
        client: dict,
        model: str,
        keep_alive: str,
        dependencies=None,
    ) -> Tuple[dict, str, Any]:
        """Load the selected model into Ollama's memory."""
        request_id = str(uuid.uuid4())[:8]
        set_request_id(f"load-{request_id}")

        endpoint = client.get("endpoint", "")
        if not endpoint:
            raise ValueError("Client endpoint not specified")

        log.info(f"🚀 Loading model '{model}' from {endpoint}")

        try:
            data = run_async(load_model(endpoint, model, keep_alive))
            result = json.dumps(data, indent=2)

            log.info(f"✅ Model '{model}' loaded successfully")
            return (client, result, dependencies)

        except Exception as e:
            log.exception(f"💥 Failed to load model '{model}': {e}")
            raise


class OllamaUnloadModel:
    """
    Unloads a model from Ollama's memory.
    Takes client and model from OllamaClient and OllamaModelSelector.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "client": ("OLLAMA_CLIENT",),
                "model": ("STRING",),
            },
            "optional": {
                "dependencies": ("*",),
            },
        }

    RETURN_TYPES = ("OLLAMA_CLIENT", "STRING", "*")
    RETURN_NAMES = ("client", "result", "dependencies")
    FUNCTION = "unload_model_op"
    CATEGORY = "Ollama"

    def unload_model_op(
        self,
        client: dict,
        model: str,
        dependencies=None,
    ) -> Tuple[dict, str, Any]:
        """Unload the selected model from Ollama's memory."""
        request_id = str(uuid.uuid4())[:8]
        set_request_id(f"unload-{request_id}")

        endpoint = client.get("endpoint", "")
        if not endpoint:
            raise ValueError("Client endpoint not specified")

        log.info(f"🗑️  Unloading model '{model}' from {endpoint}")

        try:
            data = run_async(unload_model(endpoint, model))
            result = json.dumps(data, indent=2)

            log.info(f"✅ Model '{model}' unloaded successfully")
            return (client, result, dependencies)

        except Exception as e:
            log.exception(f"💥 Failed to unload model '{model}': {e}")
            raise
