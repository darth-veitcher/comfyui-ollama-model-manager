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

# Import nodes from src package
from comfyui_ollama_model_manager.nodes import (  # noqa: E402
    OllamaLoadSelectedModel,
    OllamaRefreshModelList,
    OllamaSelectModel,
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

# Tell ComfyUI where to find our web extensions
WEB_DIRECTORY = "./web"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]

logging.info("[Ollama Manager] ✅ Loaded successfully")
