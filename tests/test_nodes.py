"""Tests for ComfyUI node classes."""

import json
from unittest.mock import patch

from comfyui_ollama_model_manager.nodes import (
    OllamaLoadSelectedModel,
    OllamaRefreshModelList,
    OllamaSelectModel,
    OllamaUnloadSelectedModel,
)


class TestOllamaRefreshModelList:
    """Tests for OllamaRefreshModelList node."""

    def test_input_types(self):
        """Test INPUT_TYPES returns correct structure."""
        input_types = OllamaRefreshModelList.INPUT_TYPES()

        assert "required" in input_types
        assert "endpoint" in input_types["required"]
        assert input_types["required"]["endpoint"][0] == "STRING"

    def test_class_attributes(self):
        """Test node class attributes."""
        assert OllamaRefreshModelList.RETURN_TYPES == ("STRING", "STRING", "*")
        assert OllamaRefreshModelList.RETURN_NAMES == (
            "models_json",
            "models_display",
            "dependencies",
        )
        assert OllamaRefreshModelList.FUNCTION == "run"
        assert OllamaRefreshModelList.CATEGORY == "Ollama"
        assert OllamaRefreshModelList.OUTPUT_NODE is True

    @patch("comfyui_ollama_model_manager.nodes.run_async")
    def test_run_success(self, mock_run_async, mock_endpoint, sample_models):
        """Test running the refresh node successfully."""
        mock_run_async.return_value = sample_models

        node = OllamaRefreshModelList()
        result = node.run(mock_endpoint)

        # Result should be a dict with "ui" and "result" keys
        assert isinstance(result, dict)
        assert "ui" in result
        assert "result" in result

        # Check UI display text
        assert "text" in result["ui"]
        display_text = result["ui"]["text"][0]
        assert isinstance(display_text, str)
        assert "Available Ollama Models" in display_text
        assert "llama3.2" in display_text
        assert "mistral" in display_text
        assert "=" in display_text  # Has separators

        # Check result tuple - now has 3 elements
        assert isinstance(result["result"], tuple)
        assert len(result["result"]) == 3

        # Parse the JSON result
        models_json = json.loads(result["result"][0])
        assert models_json == sample_models

        # models_display should match UI text
        assert result["result"][1] == display_text

        # dependencies should be None when not provided
        assert result["result"][2] is None

    @patch("comfyui_ollama_model_manager.nodes.fetch_models_from_ollama")
    @patch("comfyui_ollama_model_manager.nodes.run_async")
    def test_run_empty_models(self, mock_run_async, mock_fetch, mock_endpoint):
        """Test handling when no models are returned."""
        mock_run_async.return_value = []

        node = OllamaRefreshModelList()
        result = node.run(mock_endpoint)

        # Check result structure
        models_json = json.loads(result["result"][0])
        assert models_json == ["<no-models-returned>"]

        # Check display shows the placeholder
        display_text = result["ui"]["text"][0]
        assert "<no-models-returned>" in display_text

        assert result["result"][2] is None


class TestOllamaSelectModel:
    """Tests for OllamaSelectModel node."""

    def test_input_types_with_cache(self, populated_cache):
        """Test INPUT_TYPES with populated cache."""
        input_types = OllamaSelectModel.INPUT_TYPES()

        assert "required" in input_types
        assert "model" in input_types["required"]
        assert "optional" in input_types
        assert "models_json" in input_types["optional"]

        # Model input should be STRING type
        model_input = input_types["required"]["model"]
        assert model_input[0] == "STRING"

    def test_input_types_empty_cache(self):
        """Test INPUT_TYPES with empty cache."""
        # Make sure cache is empty
        from comfyui_ollama_model_manager.state import set_models

        set_models("http://localhost:11434", [])

        input_types = OllamaSelectModel.INPUT_TYPES()
        model_input = input_types["required"]["model"]

        # Should be STRING type with empty default
        assert model_input[0] == "STRING"
        assert model_input[1]["default"] == ""

    def test_run(self, populated_cache):
        """Test running the select node."""
        node = OllamaSelectModel()
        result = node.run("llama3.2")

        assert result == ("llama3.2", None)


class TestOllamaLoadSelectedModel:
    """Tests for OllamaLoadSelectedModel node."""

    def test_input_types(self, populated_cache):
        """Test INPUT_TYPES returns correct structure."""
        input_types = OllamaLoadSelectedModel.INPUT_TYPES()

        assert "required" in input_types
        assert "endpoint" in input_types["required"]
        assert "model" in input_types["required"]
        assert "keep_alive" in input_types["required"]

    @patch("comfyui_ollama_model_manager.nodes.run_async")
    def test_run_success(self, mock_run_async, mock_endpoint, populated_cache):
        """Test loading a model successfully."""
        mock_run_async.return_value = {"status": "success"}

        node = OllamaLoadSelectedModel()
        result = node.run(mock_endpoint, "llama3.2", "-1")

        assert isinstance(result, tuple)
        assert len(result) == 2

        result_json = json.loads(result[0])
        assert result_json == {"status": "success"}
        assert result[1] is None


class TestOllamaUnloadSelectedModel:
    """Tests for OllamaUnloadSelectedModel node."""

    def test_input_types(self, populated_cache):
        """Test INPUT_TYPES returns correct structure."""
        input_types = OllamaUnloadSelectedModel.INPUT_TYPES()

        assert "required" in input_types
        assert "endpoint" in input_types["required"]
        assert "model" in input_types["required"]
        # Should NOT have keep_alive
        assert "keep_alive" not in input_types["required"]

    @patch("comfyui_ollama_model_manager.nodes.run_async")
    def test_run_success(self, mock_run_async, mock_endpoint, populated_cache):
        """Test unloading a model successfully."""
        mock_run_async.return_value = {"status": "success"}

        node = OllamaUnloadSelectedModel()
        result = node.run(mock_endpoint, "llama3.2")

        assert isinstance(result, tuple)
        assert len(result) == 2

        result_json = json.loads(result[0])
        assert result_json == {"status": "success"}
        assert result[1] is None


def test_node_registration():
    """Test that all nodes are properly registered."""
    from comfyui_ollama_model_manager import (
        NODE_CLASS_MAPPINGS,
        NODE_DISPLAY_NAME_MAPPINGS,
    )

    expected_nodes = [
        "OllamaRefreshModelList",
        "OllamaSelectModel",
        "OllamaLoadSelectedModel",
        "OllamaUnloadSelectedModel",
    ]

    for node_name in expected_nodes:
        assert node_name in NODE_CLASS_MAPPINGS
        assert node_name in NODE_DISPLAY_NAME_MAPPINGS
        assert NODE_CLASS_MAPPINGS[node_name] is not None
        assert isinstance(NODE_DISPLAY_NAME_MAPPINGS[node_name], str)
