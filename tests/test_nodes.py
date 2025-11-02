"""Tests for ComfyUI node classes."""

import json
from unittest.mock import patch

from comfyui_ollama_model_manager.nodes import (
    OllamaClient,
    OllamaLoadModel,
    OllamaModelSelector,
    OllamaUnloadModel,
)


class TestOllamaClient:
    """Tests for OllamaClient node."""

    def test_input_types(self):
        """Test INPUT_TYPES returns correct structure."""
        input_types = OllamaClient.INPUT_TYPES()

        assert "required" in input_types
        assert "endpoint" in input_types["required"]

    def test_class_attributes(self):
        """Test node class attributes."""
        assert OllamaClient.RETURN_TYPES == ("OLLAMA_CLIENT",)
        assert OllamaClient.RETURN_NAMES == ("client",)
        assert OllamaClient.FUNCTION == "create_client"
        assert OllamaClient.CATEGORY == "Ollama"

    def test_create_client(self, mock_endpoint):
        """Test creating client config."""
        node = OllamaClient()
        result = node.create_client(mock_endpoint)

        assert isinstance(result, tuple)
        assert len(result) == 1

        client = result[0]
        assert isinstance(client, dict)
        assert client["endpoint"] == mock_endpoint
        assert client["type"] == "ollama_client"


class TestOllamaModelSelector:
    """Tests for OllamaModelSelector node."""

    def test_input_types(self):
        """Test INPUT_TYPES returns correct structure."""
        input_types = OllamaModelSelector.INPUT_TYPES()

        assert "required" in input_types
        assert "client" in input_types["required"]
        assert "model" in input_types["required"]
        assert "optional" in input_types
        assert "refresh" in input_types["optional"]

    def test_class_attributes(self):
        """Test node class attributes."""
        assert OllamaModelSelector.RETURN_TYPES == ("OLLAMA_CLIENT", "STRING", "STRING")
        assert OllamaModelSelector.RETURN_NAMES == ("client", "model", "models_json")
        assert OllamaModelSelector.FUNCTION == "select_model"
        assert OllamaModelSelector.CATEGORY == "Ollama"
        assert OllamaModelSelector.OUTPUT_NODE is True

    @patch("comfyui_ollama_model_manager.nodes.run_async")
    def test_select_model_with_refresh(
        self, mock_run_async, mock_endpoint, sample_models
    ):
        """Test selecting model with refresh."""
        mock_run_async.return_value = sample_models

        client = {"endpoint": mock_endpoint, "type": "ollama_client"}
        node = OllamaModelSelector()
        result = node.select_model(client, "llama3.2", True)

        # Should return dict with ui and result
        assert isinstance(result, dict)
        assert "ui" in result
        assert "result" in result

        # Check result tuple
        result_tuple = result["result"]
        assert len(result_tuple) == 3
        assert result_tuple[0] == client
        assert result_tuple[1] == "llama3.2"
        models_json = json.loads(result_tuple[2])
        assert len(models_json) == len(sample_models)

        # Verify mock was called (refresh happened)
        mock_run_async.assert_called_once()

    @patch("comfyui_ollama_model_manager.nodes.set_models")
    def test_select_model_without_refresh(
        self, mock_set_models, mock_endpoint, sample_models
    ):
        """Test selecting model without refresh - uses cached models."""
        # Pre-populate cache
        from comfyui_ollama_model_manager.state import set_models

        set_models(mock_endpoint, sample_models)

        client = {"endpoint": mock_endpoint, "type": "ollama_client"}
        node = OllamaModelSelector()
        result = node.select_model(client, "llama3.2", False)

        # Should return dict with ui and result
        assert isinstance(result, dict)
        assert "ui" in result
        assert "result" in result

        result_tuple = result["result"]
        assert result_tuple[0] == client
        assert result_tuple[1] == "llama3.2"


class TestOllamaLoadModel:
    """Tests for OllamaLoadModel node."""

    def test_input_types(self):
        """Test INPUT_TYPES returns correct structure."""
        input_types = OllamaLoadModel.INPUT_TYPES()

        assert "required" in input_types
        assert "client" in input_types["required"]
        assert "model" in input_types["required"]
        assert "keep_alive" in input_types["required"]

    @patch("comfyui_ollama_model_manager.nodes.run_async")
    def test_load_model_success(self, mock_run_async, mock_endpoint):
        """Test loading a model successfully."""
        mock_run_async.return_value = {"status": "success"}

        client = {"endpoint": mock_endpoint, "type": "ollama_client"}
        node = OllamaLoadModel()
        result = node.load_model_op(client, "llama3.2", "-1")

        assert isinstance(result, tuple)
        assert len(result) == 3
        assert result[0] == client

        result_json = json.loads(result[1])
        assert result_json == {"status": "success"}
        assert result[2] is None


class TestOllamaUnloadModel:
    """Tests for OllamaUnloadModel node."""

    def test_input_types(self):
        """Test INPUT_TYPES returns correct structure."""
        input_types = OllamaUnloadModel.INPUT_TYPES()

        assert "required" in input_types
        assert "client" in input_types["required"]
        assert "model" in input_types["required"]
        # Should NOT have keep_alive
        assert "keep_alive" not in input_types["required"]

    @patch("comfyui_ollama_model_manager.nodes.run_async")
    def test_unload_model_success(self, mock_run_async, mock_endpoint):
        """Test unloading a model successfully."""
        mock_run_async.return_value = {"status": "success"}

        client = {"endpoint": mock_endpoint, "type": "ollama_client"}
        node = OllamaUnloadModel()
        result = node.unload_model_op(client, "llama3.2")

        assert isinstance(result, tuple)
        assert len(result) == 3
        assert result[0] == client

        result_json = json.loads(result[1])
        assert result_json == {"status": "success"}
        assert result[2] is None


def test_node_registration():
    """Test that all nodes are properly registered."""
    from comfyui_ollama_model_manager import (
        NODE_CLASS_MAPPINGS,
        NODE_DISPLAY_NAME_MAPPINGS,
    )

    expected_nodes = [
        "OllamaClient",
        "OllamaModelSelector",
        "OllamaLoadModel",
        "OllamaUnloadModel",
    ]

    # Verify we have exactly 4 nodes
    assert (
        len(NODE_CLASS_MAPPINGS) == 4
    ), f"Expected 4 nodes, got {len(NODE_CLASS_MAPPINGS)}"

    for node_name in expected_nodes:
        assert (
            node_name in NODE_CLASS_MAPPINGS
        ), f"{node_name} not in NODE_CLASS_MAPPINGS"
        assert (
            node_name in NODE_DISPLAY_NAME_MAPPINGS
        ), f"{node_name} not in NODE_DISPLAY_NAME_MAPPINGS"
        assert NODE_CLASS_MAPPINGS[node_name] is not None
        assert isinstance(NODE_DISPLAY_NAME_MAPPINGS[node_name], str)
