"""Chat completion nodes for Ollama integration."""

from typing import Any, Dict, List, Tuple

from .async_utils import run_async
from .log_config import get_logger
from .ollama_client import chat_completion
from .types import OllamaIO

log = get_logger()


class OllamaChatCompletion:
    """
    Generate chat completions using Ollama models.

    This node provides text generation with conversation history management,
    system prompts, and configurable generation parameters. It integrates
    seamlessly with OllamaClient and OllamaModelSelector nodes.

    Supports:
    - Multi-turn conversations via history
    - System prompts for behavior control
    - Optional generation parameters (temperature, seed, etc.)
    - Vision models via image input
    """

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        """
        Define input parameters for the chat completion node.

        Returns:
            Dict specifying required and optional inputs with their types
        """
        return {
            "required": {
                "client": (
                    OllamaIO.CLIENT,
                    {
                        "tooltip": "Ollama client connection from OllamaClient or OllamaModelSelector node",
                    },
                ),
                "model": (
                    "STRING",
                    {
                        "default": "",
                        "tooltip": "Model name to use for generation (auto-populated from selector)",
                    },
                ),
                "prompt": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                        "tooltip": "User prompt or question to send to the model",
                    },
                ),
            },
            "optional": {
                "system_prompt": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                        "tooltip": "System instructions to guide model behavior (optional)",
                    },
                ),
                "history": (
                    OllamaIO.HISTORY,
                    {
                        "tooltip": "Conversation history from previous chat turns (optional)",
                    },
                ),
                "options": (
                    OllamaIO.OPTIONS,
                    {
                        "tooltip": "Generation parameters like temperature, seed, etc. (optional)",
                    },
                ),
                "format": (
                    ["none", "json"],
                    {
                        "default": "none",
                        "tooltip": "Output format: 'none' for text, 'json' for structured JSON response",
                    },
                ),
                "image": (
                    "IMAGE",
                    {
                        "tooltip": "Image input for vision models (optional)",
                    },
                ),
            },
        }

    RETURN_TYPES = ("STRING", OllamaIO.HISTORY)
    RETURN_NAMES = ("response", "history")
    FUNCTION = "generate"
    CATEGORY = "Ollama"

    @classmethod
    def IS_CHANGED(cls, **kwargs) -> float:
        """
        Cache behavior based on seed presence.

        If options contain a seed, the node will cache results (like standard ComfyUI nodes).
        If no seed is present, returns NaN to force re-execution for non-deterministic generation.

        This prevents unnecessary LLM calls when using deterministic generation with a seed.

        Args:
            **kwargs: Input parameters from the node

        Returns:
            NaN if no seed (always re-execute), or stable hash if seed present (cache results)
        """
        options = kwargs.get("options")

        # If options exist and contain a seed, allow caching by returning a stable value
        if options and isinstance(options, dict) and "seed" in options:
            # Return a hash of all inputs for cache key
            # This allows ComfyUI to cache results when inputs are identical
            import hashlib
            import json

            client = kwargs.get("client", {})
            history = kwargs.get("history", [])
            image = kwargs.get("image")

            cache_data = {
                "endpoint": (
                    client.get("endpoint", "") if isinstance(client, dict) else ""
                ),
                "model": kwargs.get("model", ""),
                "prompt": kwargs.get("prompt", ""),
                "system_prompt": kwargs.get("system_prompt", ""),
                "format": kwargs.get("format", "none"),
                "options": options,
                "history": history if history else [],
            }

            # Include image hash if present (don't include full tensor in cache key)
            if image is not None:
                cache_data["has_image"] = True

            cache_key = json.dumps(cache_data, sort_keys=True)
            # Use hashlib for stable hash across sessions (Python's hash() is randomized)
            return hashlib.sha256(cache_key.encode()).hexdigest()

        # No seed present - return NaN to force re-execution (non-deterministic)
        return float("nan")

    @classmethod
    def VALIDATE_INPUTS(cls, **kwargs) -> bool | str:
        """
        Validate input parameters before execution.

        Args:
            **kwargs: Input parameters from the node

        Returns:
            True if valid, error message string if invalid
        """
        # Note: We intentionally don't validate model or prompt here because:
        # 1. Empty model validation happens at ComfyUI's node connection level
        # 2. Empty strings are valid for optional text inputs (system_prompt)
        # 3. Validation errors were being incorrectly applied to all fields
        # Let the actual execution handle missing required values
        return True

    def generate(
        self,
        client: Dict[str, str],
        model: str,
        prompt: str,
        system_prompt: str | None = None,
        history: List[Dict[str, str]] | None = None,
        options: Dict[str, Any] | None = None,
        format: str = "none",
        image: Any = None,
    ) -> Tuple[str, List[Dict[str, str]]]:
        """
        Generate chat completion using Ollama.

        Args:
            client: Ollama client dict with 'endpoint' key
            model: Name of the model to use
            prompt: User prompt/question
            system_prompt: Optional system instructions
            history: Optional conversation history (list of message dicts)
            options: Optional generation parameters
            format: Output format - 'none' for text or 'json' for JSON mode
            image: Optional image tensor for vision models

        Returns:
            Tuple of (response_text, updated_history)
        """
        endpoint = client.get("endpoint", "")
        if not endpoint:
            raise ValueError("Client endpoint is missing or empty")

        # Build messages list from history and new prompt
        messages: List[Dict[str, str]] = []

        # Add previous messages from history
        if history:
            messages.extend(history)

        # Add system prompt if provided and not already in history
        if system_prompt is not None and system_prompt.strip():
            # Only add system prompt if it's not already the first message
            if not messages or messages[0].get("role") != "system":
                messages.insert(
                    0,
                    {
                        "role": "system",
                        "content": system_prompt.strip(),
                    },
                )

        # Add current user prompt
        messages.append(
            {
                "role": "user",
                "content": prompt.strip(),
            }
        )

        # Convert image if provided
        images = None
        if image is not None:
            images = self._convert_image_to_base64(image)

        log.info(f"💬 Generating response with {len(messages)} messages")

        # Prepare format parameter for Ollama API
        format_param = format if format != "none" else None

        # Call Ollama chat API
        result = run_async(
            chat_completion(
                endpoint=endpoint,
                model=model,
                messages=messages,
                options=options,
                images=images,
                format=format_param,
            )
        )

        # Extract response
        assistant_message = result.get("message", {})
        response_text = assistant_message.get("content", "")

        # Update history with assistant response
        updated_history = messages.copy()
        updated_history.append(
            {
                "role": "assistant",
                "content": response_text,
            }
        )

        log.info(f"✅ Generated response ({len(response_text)} chars)")

        return (response_text, updated_history)

    def _convert_image_to_base64(self, image: Any) -> List[str]:
        """
        Convert ComfyUI image tensor to base64 PNG for Ollama.

        Args:
            image: ComfyUI IMAGE tensor (batch, height, width, channels)

        Returns:
            List of base64-encoded PNG strings
        """
        import base64
        from io import BytesIO

        import numpy as np
        from PIL import Image

        images_b64 = []

        # ComfyUI images are tensors with shape (batch, height, width, channels)
        # Values are typically in range [0, 1]
        if not isinstance(image, np.ndarray):
            # Convert torch tensor to numpy if needed
            try:
                image = image.cpu().numpy()
            except Exception:
                pass

        # Handle single image or batch
        if len(image.shape) == 3:
            # Single image: (height, width, channels)
            image = np.expand_dims(image, 0)

        # Process each image in batch
        for img_array in image:
            # Convert from [0, 1] to [0, 255]
            if img_array.max() <= 1.0:
                img_array = (img_array * 255).astype(np.uint8)

            # Convert to PIL Image
            pil_image = Image.fromarray(img_array)

            # Convert to PNG bytes
            buffer = BytesIO()
            pil_image.save(buffer, format="PNG")
            buffer.seek(0)

            # Encode as base64
            img_b64 = base64.b64encode(buffer.read()).decode("utf-8")
            images_b64.append(img_b64)

        return images_b64


class OllamaDebugHistory:
    """
    Debug node to inspect conversation history.

    This utility node helps visualize and debug conversation history
    by converting it to a formatted string. Useful for:
    - Understanding conversation flow
    - Debugging history issues
    - Inspecting message structure
    """

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        return {
            "required": {
                "history": (
                    OllamaIO.HISTORY,
                    {
                        "tooltip": "Conversation history to inspect",
                    },
                ),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("formatted_history",)
    FUNCTION = "format_history"
    CATEGORY = "Ollama/Debug"
    OUTPUT_NODE = True

    def format_history(self, history: List[Dict[str, str]]) -> Tuple[str]:
        """
        Format conversation history as readable text.

        Args:
            history: List of message dicts from conversation

        Returns:
            Tuple containing formatted history string
        """
        if not history:
            return ("(Empty history)",)

        lines = []
        lines.append(f"=== Conversation History ({len(history)} messages) ===\n")

        for i, msg in enumerate(history, 1):
            role = msg.get("role", "unknown")
            content = msg.get("content", "")

            # Truncate very long messages
            if len(content) > 200:
                content = content[:200] + "..."

            lines.append(f"[{i}] {role.upper()}:")
            lines.append(f"    {content}\n")

        formatted = "\n".join(lines)
        log.debug(f"Formatted history: {len(history)} messages")

        return (formatted,)


class OllamaHistoryLength:
    """
    Get the number of messages in conversation history.

    Useful for conditional workflows or debugging.
    """

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        return {
            "required": {
                "history": (
                    OllamaIO.HISTORY,
                    {
                        "tooltip": "Conversation history to count",
                    },
                ),
            },
        }

    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("length",)
    FUNCTION = "get_length"
    CATEGORY = "Ollama/Debug"

    def get_length(self, history: List[Dict[str, str]]) -> Tuple[int]:
        """
        Get the number of messages in history.

        Args:
            history: Conversation history

        Returns:
            Tuple containing message count
        """
        if not history:
            return (0,)
        return (len(history),)


# Node mappings for ComfyUI registration
NODE_CLASS_MAPPINGS = {
    "OllamaChatCompletion": OllamaChatCompletion,
    "OllamaDebugHistory": OllamaDebugHistory,
    "OllamaHistoryLength": OllamaHistoryLength,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "OllamaChatCompletion": "Ollama Chat Completion",
    "OllamaDebugHistory": "Ollama Debug: History",
    "OllamaHistoryLength": "Ollama Debug: History Length",
}
