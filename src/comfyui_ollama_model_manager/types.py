"""Custom I/O types for Ollama nodes.

This module defines custom types used for type-safe connections between nodes
in the ComfyUI workflow graph.
"""


class OllamaIO:
    """Custom I/O type identifiers for Ollama nodes.
    
    These types ensure that outputs from one node can only be connected
    to compatible inputs on other nodes, providing type safety in the
    ComfyUI workflow graph.
    
    Attributes:
        CLIENT: Connection type for Ollama client instances
        OPTIONS: Connection type for generation parameters (temperature, seed, etc.)
        HISTORY: Connection type for conversation history (list of messages)
    """
    
    CLIENT = "OLLAMA_CLIENT"
    OPTIONS = "OLLAMA_OPTIONS"
    HISTORY = "OLLAMA_HISTORY"
