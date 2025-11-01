"""ComfyUI node definitions for Ollama model management."""

import json
import uuid
from typing import Tuple

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
    CATEGORY = "Ollama/Enum"

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
    Present cached models as a dropdown.
    
    This node dynamically updates its dropdown based on the cached models.
    ComfyUI will re-query INPUT_TYPES when IS_CHANGED indicates a change.
    """

    @classmethod
    def INPUT_TYPES(cls):
        models = get_models()
        if not models:
            # User hasn't refreshed yet
            models = ["<run-OllamaRefreshModelList-first>"]
        return {
            "required": {
                "model": (
                    models,
                    {"default": models[0]},
                ),
            }
        }

    @classmethod
    def IS_CHANGED(cls, model):
        """Force UI to re-query INPUT_TYPES when models cache changes."""
        # Return a hash of the current models list
        # When this changes, ComfyUI will re-query INPUT_TYPES
        models = get_models()
        return str(hash(tuple(models)))

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("model",)
    FUNCTION = "run"
    CATEGORY = "Ollama/Enum"

    def run(self, model: str) -> Tuple[str]:
        """Select a model from the cached list."""
        request_id = str(uuid.uuid4())[:8]
        set_request_id(f"select-{request_id}")
        
        log.info(f"🎯 Selected model: '{model}'")
        
        # Just echo the selection forward
        return (model,)


class OllamaLoadSelectedModel:
    """
    Loads a model that was selected from OllamaSelectModel.

    You can also override the endpoint here in case the refresh node pointed
    at a different server.
    """

    @classmethod
    def INPUT_TYPES(cls):
        # We re-use the cached list to offer another enum here
        models = get_models()
        if not models:
            models = ["<run-OllamaRefreshModelList-first>"]
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
                    models,
                    {"default": models[0]},
                ),
                "keep_alive": (
                    "STRING",
                    {
                        "default": "-1",
                        "multiline": False,
                    },
                ),
            }
        }

    @classmethod
    def IS_CHANGED(cls, endpoint, model, keep_alive):
        """Force UI to re-query INPUT_TYPES when models cache changes."""
        models = get_models()
        return str(hash(tuple(models)))

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)
    FUNCTION = "run"
    CATEGORY = "Ollama/Enum"

    def run(self, endpoint: str, model: str, keep_alive: str) -> Tuple[str]:
        """Load the selected model into Ollama's memory."""
        request_id = str(uuid.uuid4())[:8]
        set_request_id(f"load-{request_id}")
        
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
    Unloads a model selected from the cached list (keep_alive=0).
    """

    @classmethod
    def INPUT_TYPES(cls):
        models = get_models()
        if not models:
            models = ["<run-OllamaRefreshModelList-first>"]
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
                    models,
                    {"default": models[0]},
                ),
            }
        }

    @classmethod
    def IS_CHANGED(cls, endpoint, model):
        """Force UI to re-query INPUT_TYPES when models cache changes."""
        models = get_models()
        return str(hash(tuple(models)))

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)
    FUNCTION = "run"
    CATEGORY = "Ollama/Enum"

    def run(self, endpoint: str, model: str) -> Tuple[str]:
        """Unload the selected model from Ollama's memory."""
        request_id = str(uuid.uuid4())[:8]
        set_request_id(f"unload-{request_id}")
        
        log.info(f"🗑️  Unloading model '{model}' from {endpoint}")
        
        try:
            data = run_async(unload_model(endpoint, model))
            result = json.dumps(data, indent=2)
            
            log.info(f"✅ Model '{model}' unloaded successfully")
            return (result,)
            
        except Exception as e:
            log.exception(f"💥 Failed to unload model '{model}': {e}")
            raise
