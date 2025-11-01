"""ComfyUI Ollama Model Manager - Node registration."""

from comfyui_ollama_model_manager.nodes import (
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

__all__ = [
    "OllamaRefreshModelList",
    "OllamaSelectModel",
    "OllamaLoadSelectedModel",
    "OllamaUnloadSelectedModel",
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
]
