"""
@author: darth-veitcher
@title: ComfyUI Ollama Model Manager
@nickname: Ollama Manager
@description: Custom nodes for managing Ollama models in ComfyUI workflows. Load and unload models on-demand to optimize memory usage.
"""

import logging
import os
import sys

# Add src directory to path for imports
custom_nodes_path = os.path.dirname(__file__)
src_path = os.path.join(custom_nodes_path, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Check and install dependencies if needed
try:
    import httpx  # noqa: F401
    import loguru  # noqa: F401
    import rich  # noqa: F401
except ImportError:
    logging.warning("[Ollama Manager] Dependencies not found, attempting to install...")
    try:
        # Import and run the installer
        install_path = os.path.join(custom_nodes_path, "install.py")
        if os.path.exists(install_path):
            # Run install.py as a module
            import importlib.util

            spec = importlib.util.spec_from_file_location("install", install_path)
            if spec and spec.loader:
                install_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(install_module)
                install_module.install_dependencies()  # type: ignore

                # Try importing again
                import httpx  # noqa: F401
                import loguru  # noqa: F401
                import rich  # noqa: F401

                logging.info("[Ollama Manager] ✅ Dependencies installed successfully")
            else:
                raise ImportError("Could not load install.py")
        else:
            raise ImportError("install.py not found")
    except Exception as e:
        logging.error(
            f"[Ollama Manager] ❌ Failed to install dependencies: {e}\n"
            "Please install manually: pip install httpx loguru rich"
        )
        raise ImportError(
            "Required dependencies not installed. " "Run: pip install httpx loguru rich"
        ) from e

# Register API routes for CORS-free model fetching
from comfyui_ollama_model_manager.api import setup_api_routes  # noqa: E402
from comfyui_ollama_model_manager.chat import (  # noqa: E402
    OllamaChatCompletion,
    OllamaDebugHistory,
    OllamaHistoryLength,
)

# Import nodes from src package
from comfyui_ollama_model_manager.nodes import (  # noqa: E402
    OllamaClient,
    OllamaLoadModel,
    OllamaModelSelector,
    OllamaUnloadModel,
)

# Import option nodes
from comfyui_ollama_model_manager.options import (  # noqa: E402
    OllamaOptionExtraBody,
    OllamaOptionMaxTokens,
    OllamaOptionRepeatPenalty,
    OllamaOptionSeed,
    OllamaOptionTemperature,
    OllamaOptionTopK,
    OllamaOptionTopP,
)

setup_api_routes()

# Register nodes with ComfyUI
NODE_CLASS_MAPPINGS = {
    "OllamaClient": OllamaClient,
    "OllamaModelSelector": OllamaModelSelector,
    "OllamaLoadModel": OllamaLoadModel,
    "OllamaUnloadModel": OllamaUnloadModel,
    "OllamaChatCompletion": OllamaChatCompletion,
    "OllamaDebugHistory": OllamaDebugHistory,
    "OllamaHistoryLength": OllamaHistoryLength,
    "OllamaOptionTemperature": OllamaOptionTemperature,
    "OllamaOptionSeed": OllamaOptionSeed,
    "OllamaOptionMaxTokens": OllamaOptionMaxTokens,
    "OllamaOptionTopP": OllamaOptionTopP,
    "OllamaOptionTopK": OllamaOptionTopK,
    "OllamaOptionRepeatPenalty": OllamaOptionRepeatPenalty,
    "OllamaOptionExtraBody": OllamaOptionExtraBody,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "OllamaClient": "Ollama Client",
    "OllamaModelSelector": "Ollama Model Selector",
    "OllamaLoadModel": "Ollama Load Model",
    "OllamaUnloadModel": "Ollama Unload Model",
    "OllamaChatCompletion": "Ollama Chat Completion",
    "OllamaDebugHistory": "Ollama Debug: History",
    "OllamaHistoryLength": "Ollama Debug: History Length",
    "OllamaOptionTemperature": "Ollama Option: Temperature",
    "OllamaOptionSeed": "Ollama Option: Seed",
    "OllamaOptionMaxTokens": "Ollama Option: Max Tokens",
    "OllamaOptionTopP": "Ollama Option: Top P",
    "OllamaOptionTopK": "Ollama Option: Top K",
    "OllamaOptionRepeatPenalty": "Ollama Option: Repeat Penalty",
    "OllamaOptionExtraBody": "Ollama Option: Extra Body",
}

# Tell ComfyUI where to find our web extensions
WEB_DIRECTORY = "./web"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]

logging.info("[Ollama Manager] ✅ Loaded successfully")
