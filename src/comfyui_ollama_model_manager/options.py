"""Composable option nodes for Ollama chat generation parameters.

These nodes follow the merge pattern from comfyui-openai-api, allowing users
to chain multiple option nodes together to build a complete set of generation
parameters.

Example workflow:
    [Temperature=0.7] → [Seed=42] → [MaxTokens=100] → [Chat Completion]
                            ↓           ↓           ↓
                        (merged options dict)
"""

from typing import Any, Dict, Tuple

from .types import OllamaIO


class OllamaOptionTemperature:
    """
    Control randomness in generation.
    
    Temperature affects how the model samples tokens:
    - 0.0 = Deterministic (always picks most likely token)
    - 0.8 = Balanced (default)
    - 2.0 = Very creative/random
    
    Higher values make output more random, lower values make it more focused.
    """

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        return {
            "required": {
                "temperature": (
                    "FLOAT",
                    {
                        "default": 0.8,
                        "min": 0.0,
                        "max": 2.0,
                        "step": 0.01,
                        "tooltip": "Controls randomness: 0.0=deterministic, 0.8=balanced, 2.0=very random",
                    },
                ),
            },
            "optional": {
                "options": (
                    OllamaIO.OPTIONS,
                    {
                        "tooltip": "Other options to merge with (optional)",
                    },
                ),
            },
        }

    RETURN_TYPES = (OllamaIO.OPTIONS,)
    RETURN_NAMES = ("options",)
    FUNCTION = "merge"
    CATEGORY = "Ollama/Options"

    def merge(
        self, temperature: float, options: Dict[str, Any] | None = None
    ) -> Tuple[Dict[str, Any]]:
        """Merge temperature into options dict."""
        if options is None:
            options = {}
        else:
            options = options.copy()
        options["temperature"] = temperature
        return (options,)


class OllamaOptionSeed:
    """
    Set random seed for reproducible generation.
    
    When set, the same prompt with the same seed will produce the same output
    (assuming other parameters are identical). Useful for:
    - Testing and debugging
    - Reproducible results
    - Comparing different prompts with same randomness
    """

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        return {
            "required": {
                "seed": (
                    "INT",
                    {
                        "default": 42,
                        "min": 0,
                        "max": 2**31 - 1,
                        "tooltip": "Random seed for reproducible generation",
                    },
                ),
            },
            "optional": {
                "options": (
                    OllamaIO.OPTIONS,
                    {
                        "tooltip": "Other options to merge with (optional)",
                    },
                ),
            },
        }

    RETURN_TYPES = (OllamaIO.OPTIONS,)
    RETURN_NAMES = ("options",)
    FUNCTION = "merge"
    CATEGORY = "Ollama/Options"

    def merge(
        self, seed: int, options: Dict[str, Any] | None = None
    ) -> Tuple[Dict[str, Any]]:
        """Merge seed into options dict."""
        if options is None:
            options = {}
        else:
            options = options.copy()
        options["seed"] = seed
        return (options,)


class OllamaOptionMaxTokens:
    """
    Limit maximum tokens to generate.
    
    Controls the length of the generated response. In Ollama, this maps to
    the 'num_predict' parameter.
    
    Note: This is a maximum limit, not a target. The model may generate
    fewer tokens if it reaches a natural stopping point.
    """

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        return {
            "required": {
                "max_tokens": (
                    "INT",
                    {
                        "default": 128,
                        "min": 1,
                        "max": 4096,
                        "step": 1,
                        "tooltip": "Maximum number of tokens to generate (Ollama: num_predict)",
                    },
                ),
            },
            "optional": {
                "options": (
                    OllamaIO.OPTIONS,
                    {
                        "tooltip": "Other options to merge with (optional)",
                    },
                ),
            },
        }

    RETURN_TYPES = (OllamaIO.OPTIONS,)
    RETURN_NAMES = ("options",)
    FUNCTION = "merge"
    CATEGORY = "Ollama/Options"

    def merge(
        self, max_tokens: int, options: Dict[str, Any] | None = None
    ) -> Tuple[Dict[str, Any]]:
        """Merge max_tokens (num_predict) into options dict."""
        if options is None:
            options = {}
        else:
            options = options.copy()
        # Ollama uses 'num_predict' for max tokens
        options["num_predict"] = max_tokens
        return (options,)


class OllamaOptionTopP:
    """
    Control nucleus sampling.
    
    Top-p (nucleus) sampling considers the smallest set of tokens whose
    cumulative probability exceeds p. This is an alternative to temperature
    for controlling randomness.
    
    - 1.0 = Consider all tokens (default)
    - 0.9 = Consider top 90% probability mass
    - 0.5 = Consider top 50% probability mass (more focused)
    """

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        return {
            "required": {
                "top_p": (
                    "FLOAT",
                    {
                        "default": 0.9,
                        "min": 0.0,
                        "max": 1.0,
                        "step": 0.01,
                        "tooltip": "Nucleus sampling: 1.0=all tokens, 0.9=top 90%, lower=more focused",
                    },
                ),
            },
            "optional": {
                "options": (
                    OllamaIO.OPTIONS,
                    {
                        "tooltip": "Other options to merge with (optional)",
                    },
                ),
            },
        }

    RETURN_TYPES = (OllamaIO.OPTIONS,)
    RETURN_NAMES = ("options",)
    FUNCTION = "merge"
    CATEGORY = "Ollama/Options"

    def merge(
        self, top_p: float, options: Dict[str, Any] | None = None
    ) -> Tuple[Dict[str, Any]]:
        """Merge top_p into options dict."""
        if options is None:
            options = {}
        else:
            options = options.copy()
        options["top_p"] = top_p
        return (options,)


class OllamaOptionTopK:
    """
    Control top-k sampling (Ollama-specific).
    
    Limits the number of highest probability tokens to consider for each step.
    This is an Ollama-specific parameter not available in OpenAI's API.
    
    - 40 = Consider top 40 tokens (default)
    - 10 = Very focused (only top 10 tokens)
    - 100 = More variety
    """

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        return {
            "required": {
                "top_k": (
                    "INT",
                    {
                        "default": 40,
                        "min": 1,
                        "max": 100,
                        "step": 1,
                        "tooltip": "Number of highest probability tokens to consider (Ollama-specific)",
                    },
                ),
            },
            "optional": {
                "options": (
                    OllamaIO.OPTIONS,
                    {
                        "tooltip": "Other options to merge with (optional)",
                    },
                ),
            },
        }

    RETURN_TYPES = (OllamaIO.OPTIONS,)
    RETURN_NAMES = ("options",)
    FUNCTION = "merge"
    CATEGORY = "Ollama/Options"

    def merge(
        self, top_k: int, options: Dict[str, Any] | None = None
    ) -> Tuple[Dict[str, Any]]:
        """Merge top_k into options dict."""
        if options is None:
            options = {}
        else:
            options = options.copy()
        options["top_k"] = top_k
        return (options,)


class OllamaOptionRepeatPenalty:
    """
    Penalize repetition in generation (Ollama-specific).
    
    Controls how much to penalize repeated tokens. Higher values make the
    model less likely to repeat the same phrases.
    
    - 1.0 = No penalty (default)
    - 1.1 = Slight penalty
    - 1.5 = Strong penalty against repetition
    
    This is more effective than OpenAI's frequency_penalty for Ollama models.
    """

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        return {
            "required": {
                "repeat_penalty": (
                    "FLOAT",
                    {
                        "default": 1.1,
                        "min": 0.0,
                        "max": 2.0,
                        "step": 0.01,
                        "tooltip": "Penalty for repetition: 1.0=none, 1.1=slight, 1.5=strong (Ollama-specific)",
                    },
                ),
            },
            "optional": {
                "options": (
                    OllamaIO.OPTIONS,
                    {
                        "tooltip": "Other options to merge with (optional)",
                    },
                ),
            },
        }

    RETURN_TYPES = (OllamaIO.OPTIONS,)
    RETURN_NAMES = ("options",)
    FUNCTION = "merge"
    CATEGORY = "Ollama/Options"

    def merge(
        self, repeat_penalty: float, options: Dict[str, Any] | None = None
    ) -> Tuple[Dict[str, Any]]:
        """Merge repeat_penalty into options dict."""
        if options is None:
            options = {}
        else:
            options = options.copy()
        options["repeat_penalty"] = repeat_penalty
        return (options,)


class OllamaOptionExtraBody:
    """
    Advanced Ollama parameters via JSON.
    
    Allows setting any additional Ollama parameter not covered by other nodes.
    Input should be valid JSON object.
    
    Useful parameters:
    - num_ctx: Context window size (e.g., 2048, 4096)
    - num_batch: Batch size for processing
    - num_gpu: Number of GPU layers to use
    - num_thread: Number of CPU threads
    - mirostat: Alternative sampling algorithm (0, 1, or 2)
    - mirostat_tau: Mirostat target entropy
    - mirostat_eta: Mirostat learning rate
    - stop: Stop sequences (array of strings)
    
    Example JSON:
    {"num_ctx": 4096, "num_gpu": 1, "stop": ["\\n\\n", "END"]}
    """

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        return {
            "required": {
                "extra_body": (
                    "STRING",
                    {
                        "default": "{}",
                        "multiline": True,
                        "tooltip": "JSON object with additional Ollama parameters",
                    },
                ),
            },
            "optional": {
                "options": (
                    OllamaIO.OPTIONS,
                    {
                        "tooltip": "Other options to merge with (optional)",
                    },
                ),
            },
        }

    RETURN_TYPES = (OllamaIO.OPTIONS,)
    RETURN_NAMES = ("options",)
    FUNCTION = "merge"
    CATEGORY = "Ollama/Options"

    @classmethod
    def VALIDATE_INPUTS(cls, extra_body: str, **kwargs) -> bool | str:
        """Validate that extra_body is valid JSON."""
        import json

        try:
            json.loads(extra_body)
            return True
        except json.JSONDecodeError as e:
            return f"Invalid JSON in extra_body: {e}"

    def merge(
        self, extra_body: str, options: Dict[str, Any] | None = None
    ) -> Tuple[Dict[str, Any]]:
        """Merge extra_body parameters into options dict."""
        import json

        if options is None:
            options = {}
        else:
            options = options.copy()

        # Parse JSON and merge into options
        extra_params = json.loads(extra_body)
        if isinstance(extra_params, dict):
            options.update(extra_params)

        return (options,)


# Node mappings for ComfyUI registration
NODE_CLASS_MAPPINGS = {
    "OllamaOptionTemperature": OllamaOptionTemperature,
    "OllamaOptionSeed": OllamaOptionSeed,
    "OllamaOptionMaxTokens": OllamaOptionMaxTokens,
    "OllamaOptionTopP": OllamaOptionTopP,
    "OllamaOptionTopK": OllamaOptionTopK,
    "OllamaOptionRepeatPenalty": OllamaOptionRepeatPenalty,
    "OllamaOptionExtraBody": OllamaOptionExtraBody,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "OllamaOptionTemperature": "Ollama Option: Temperature",
    "OllamaOptionSeed": "Ollama Option: Seed",
    "OllamaOptionMaxTokens": "Ollama Option: Max Tokens",
    "OllamaOptionTopP": "Ollama Option: Top P",
    "OllamaOptionTopK": "Ollama Option: Top K",
    "OllamaOptionRepeatPenalty": "Ollama Option: Repeat Penalty",
    "OllamaOptionExtraBody": "Ollama Option: Extra Body",
}
