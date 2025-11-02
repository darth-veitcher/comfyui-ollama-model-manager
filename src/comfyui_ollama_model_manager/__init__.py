"""ComfyUI Ollama Model Manager - Node registration."""

from .nodes import OllamaClient, OllamaLoadModel, OllamaModelSelector, OllamaUnloadModel

# Register nodes with ComfyUI
NODE_CLASS_MAPPINGS = {
    "OllamaClient": OllamaClient,
    "OllamaModelSelector": OllamaModelSelector,
    "OllamaLoadModel": OllamaLoadModel,
    "OllamaUnloadModel": OllamaUnloadModel,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "OllamaClient": "Ollama Client",
    "OllamaModelSelector": "Ollama Model Selector",
    "OllamaLoadModel": "Ollama Load Model",
    "OllamaUnloadModel": "Ollama Unload Model",
}

__all__ = [
    "OllamaClient",
    "OllamaModelSelector",
    "OllamaLoadModel",
    "OllamaUnloadModel",
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
]
