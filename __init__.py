"""
@author: darth-veitcher
@title: ComfyUI Ollama Model Manager
@nickname: Ollama Manager
@description: Custom nodes for managing Ollama models in ComfyUI workflows. Load and unload models on-demand to optimize memory usage.
"""

import sys
import os
import logging

# Add src directory to path for imports
custom_nodes_path = os.path.dirname(__file__)
src_path = os.path.join(custom_nodes_path, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Check dependencies
try:
    import httpx  # noqa: F401
    import loguru  # noqa: F401
except ImportError as e:
    logging.error(
        "[Ollama Manager] Missing dependencies. "
        "Please install: pip install httpx loguru rich"
    )
    raise e

# Import nodes from src package
from comfyui_ollama_model_manager.nodes import (  # noqa: E402
    OllamaRefreshModelList,
    OllamaSelectModel,
    OllamaLoadSelectedModel,
    OllamaUnloadSelectedModel,
)

# Register nodes with ComfyUI
NODE_CLASS_MAPPINGS = {
    "OllamaRefreshModelList": OllamaRefreshModelList,
    "OllamaSelectModel": OllamaSelectModel,
    "OllamaLoadSelectedModel": OllamaLoadSelectedModel,
    "OllamaUnloadSelectedModel": OllamaUnloadSelectedModel,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "OllamaRefreshModelList": "Ollama (Refresh Model List)",
    "OllamaSelectModel": "Ollama (Select Model)",
    "OllamaLoadSelectedModel": "Ollama (Load Selected Model)",
    "OllamaUnloadSelectedModel": "Ollama (Unload Selected Model)",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

logging.info("[Ollama Manager] ✅ Loaded successfully")
