"""Tests for ComfyUI node classes."""

import json
from unittest.mock import patch

from comfyui_ollama_model_manager.nodes import (
    OllamaRefreshModelList,
    OllamaSelectModel,
    OllamaLoadSelectedModel,
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
        assert OllamaRefreshModelList.RETURN_TYPES == ("STRING",)
        assert OllamaRefreshModelList.RETURN_NAMES == ("models_json",)
        assert OllamaRefreshModelList.FUNCTION == "run"
        assert OllamaRefreshModelList.CATEGORY == "Ollama/Enum"
    
    @patch("comfyui_ollama_model_manager.nodes.run_async")
    def test_run_success(self, mock_run_async, mock_endpoint, sample_models):
        """Test running the refresh node successfully."""
        mock_run_async.return_value = sample_models
        
        node = OllamaRefreshModelList()
        result = node.run(mock_endpoint)
        
        assert isinstance(result, tuple)
        assert len(result) == 1
        
        # Parse the JSON result
        models_json = json.loads(result[0])
        assert models_json == sample_models
    
    @patch("comfyui_ollama_model_manager.nodes.fetch_models_from_ollama")
    @patch("comfyui_ollama_model_manager.nodes.run_async")
    def test_run_empty_models(self, mock_run_async, mock_fetch, mock_endpoint):
        """Test handling when no models are returned."""
        mock_run_async.return_value = []
        
        node = OllamaRefreshModelList()
        result = node.run(mock_endpoint)
        
        models_json = json.loads(result[0])
        assert models_json == ["<no-models-returned>"]


class TestOllamaSelectModel:
    """Tests for OllamaSelectModel node."""
    
    def test_input_types_with_cache(self, populated_cache):
        """Test INPUT_TYPES with populated cache."""
        input_types = OllamaSelectModel.INPUT_TYPES()
        
        assert "required" in input_types
        assert "model" in input_types["required"]
        
        # Should have models from cache
        models = input_types["required"]["model"][0]
        assert isinstance(models, list)
        assert len(models) > 0
    
    def test_input_types_empty_cache(self):
        """Test INPUT_TYPES with empty cache."""
        # Make sure cache is empty
        from comfyui_ollama_model_manager.state import set_models
        set_models("http://localhost:11434", [])
        
        input_types = OllamaSelectModel.INPUT_TYPES()
        models = input_types["required"]["model"][0]
        
        assert models == ["<run-OllamaRefreshModelList-first>"]
    
    def test_run(self, populated_cache):
        """Test running the select node."""
        node = OllamaSelectModel()
        result = node.run("llama3.2")
        
        assert result == ("llama3.2",)


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
        assert len(result) == 1
        
        result_json = json.loads(result[0])
        assert result_json == {"status": "success"}


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
        assert len(result) == 1
        
        result_json = json.loads(result[0])
        assert result_json == {"status": "success"}


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
