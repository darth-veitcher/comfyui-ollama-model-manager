"""Tests for option nodes."""

import json

import pytest

from comfyui_ollama_model_manager.options import (
    OllamaOptionExtraBody,
    OllamaOptionMaxTokens,
    OllamaOptionRepeatPenalty,
    OllamaOptionSeed,
    OllamaOptionTemperature,
    OllamaOptionTopK,
    OllamaOptionTopP,
)


class TestOllamaOptionTemperature:
    """Tests for OllamaOptionTemperature node."""

    def test_input_types(self):
        """Test INPUT_TYPES structure."""
        input_types = OllamaOptionTemperature.INPUT_TYPES()
        assert "required" in input_types
        assert "optional" in input_types
        assert "temperature" in input_types["required"]
        assert "options" in input_types["optional"]

    def test_merge_without_existing_options(self):
        """Test merging temperature when no existing options."""
        node = OllamaOptionTemperature()
        result = node.merge(temperature=0.7)
        
        assert isinstance(result, tuple)
        assert len(result) == 1
        options = result[0]
        assert isinstance(options, dict)
        assert options["temperature"] == 0.7

    def test_merge_with_existing_options(self):
        """Test merging temperature with existing options."""
        node = OllamaOptionTemperature()
        existing_options = {"seed": 42, "max_tokens": 100}
        result = node.merge(temperature=0.9, options=existing_options)
        
        options = result[0]
        assert options["temperature"] == 0.9
        assert options["seed"] == 42
        assert options["max_tokens"] == 100

    def test_merge_preserves_original_dict(self):
        """Test that merge doesn't modify the original options dict."""
        node = OllamaOptionTemperature()
        existing_options = {"seed": 42}
        original_options = existing_options.copy()
        
        node.merge(temperature=0.7, options=existing_options)
        
        assert existing_options == original_options


class TestOllamaOptionSeed:
    """Tests for OllamaOptionSeed node."""

    def test_input_types(self):
        """Test INPUT_TYPES structure."""
        input_types = OllamaOptionSeed.INPUT_TYPES()
        assert "seed" in input_types["required"]
        assert "options" in input_types["optional"]

    def test_merge_seed(self):
        """Test merging seed value."""
        node = OllamaOptionSeed()
        result = node.merge(seed=123)
        
        options = result[0]
        assert options["seed"] == 123

    def test_merge_seed_with_options(self):
        """Test merging seed with existing options."""
        node = OllamaOptionSeed()
        existing = {"temperature": 0.7}
        result = node.merge(seed=456, options=existing)
        
        options = result[0]
        assert options["seed"] == 456
        assert options["temperature"] == 0.7


class TestOllamaOptionMaxTokens:
    """Tests for OllamaOptionMaxTokens node."""

    def test_input_types(self):
        """Test INPUT_TYPES structure."""
        input_types = OllamaOptionMaxTokens.INPUT_TYPES()
        assert "max_tokens" in input_types["required"]

    def test_merge_max_tokens_maps_to_num_predict(self):
        """Test that max_tokens is mapped to num_predict for Ollama."""
        node = OllamaOptionMaxTokens()
        result = node.merge(max_tokens=200)
        
        options = result[0]
        # Should use Ollama's parameter name
        assert options["num_predict"] == 200
        assert "max_tokens" not in options

    def test_merge_max_tokens_with_options(self):
        """Test merging max_tokens with existing options."""
        node = OllamaOptionMaxTokens()
        existing = {"temperature": 0.8}
        result = node.merge(max_tokens=150, options=existing)
        
        options = result[0]
        assert options["num_predict"] == 150
        assert options["temperature"] == 0.8


class TestOllamaOptionTopP:
    """Tests for OllamaOptionTopP node."""

    def test_input_types(self):
        """Test INPUT_TYPES structure."""
        input_types = OllamaOptionTopP.INPUT_TYPES()
        assert "top_p" in input_types["required"]

    def test_merge_top_p(self):
        """Test merging top_p value."""
        node = OllamaOptionTopP()
        result = node.merge(top_p=0.95)
        
        options = result[0]
        assert options["top_p"] == 0.95

    def test_merge_top_p_with_options(self):
        """Test merging top_p with existing options."""
        node = OllamaOptionTopP()
        existing = {"seed": 42}
        result = node.merge(top_p=0.85, options=existing)
        
        options = result[0]
        assert options["top_p"] == 0.85
        assert options["seed"] == 42


class TestOllamaOptionTopK:
    """Tests for OllamaOptionTopK node."""

    def test_input_types(self):
        """Test INPUT_TYPES structure."""
        input_types = OllamaOptionTopK.INPUT_TYPES()
        assert "top_k" in input_types["required"]

    def test_merge_top_k(self):
        """Test merging top_k value (Ollama-specific)."""
        node = OllamaOptionTopK()
        result = node.merge(top_k=50)
        
        options = result[0]
        assert options["top_k"] == 50

    def test_merge_top_k_with_options(self):
        """Test merging top_k with existing options."""
        node = OllamaOptionTopK()
        existing = {"temperature": 0.7}
        result = node.merge(top_k=30, options=existing)
        
        options = result[0]
        assert options["top_k"] == 30
        assert options["temperature"] == 0.7


class TestOllamaOptionRepeatPenalty:
    """Tests for OllamaOptionRepeatPenalty node."""

    def test_input_types(self):
        """Test INPUT_TYPES structure."""
        input_types = OllamaOptionRepeatPenalty.INPUT_TYPES()
        assert "repeat_penalty" in input_types["required"]

    def test_merge_repeat_penalty(self):
        """Test merging repeat_penalty value (Ollama-specific)."""
        node = OllamaOptionRepeatPenalty()
        result = node.merge(repeat_penalty=1.2)
        
        options = result[0]
        assert options["repeat_penalty"] == 1.2

    def test_merge_repeat_penalty_with_options(self):
        """Test merging repeat_penalty with existing options."""
        node = OllamaOptionRepeatPenalty()
        existing = {"seed": 123}
        result = node.merge(repeat_penalty=1.5, options=existing)
        
        options = result[0]
        assert options["repeat_penalty"] == 1.5
        assert options["seed"] == 123


class TestOllamaOptionExtraBody:
    """Tests for OllamaOptionExtraBody node."""

    def test_input_types(self):
        """Test INPUT_TYPES structure."""
        input_types = OllamaOptionExtraBody.INPUT_TYPES()
        assert "extra_body" in input_types["required"]

    def test_validate_valid_json(self):
        """Test that valid JSON passes validation."""
        result = OllamaOptionExtraBody.VALIDATE_INPUTS(
            extra_body='{"num_ctx": 2048}'
        )
        assert result is True

    def test_validate_invalid_json(self):
        """Test that invalid JSON fails validation."""
        result = OllamaOptionExtraBody.VALIDATE_INPUTS(
            extra_body='{invalid json}'
        )
        assert isinstance(result, str)
        assert "Invalid JSON" in result

    def test_merge_extra_body_simple(self):
        """Test merging simple JSON parameters."""
        node = OllamaOptionExtraBody()
        extra_body = json.dumps({"num_ctx": 4096, "num_gpu": 1})
        result = node.merge(extra_body=extra_body)
        
        options = result[0]
        assert options["num_ctx"] == 4096
        assert options["num_gpu"] == 1

    def test_merge_extra_body_with_existing_options(self):
        """Test merging extra_body with existing options."""
        node = OllamaOptionExtraBody()
        existing = {"temperature": 0.7, "seed": 42}
        extra_body = json.dumps({"num_ctx": 2048, "stop": ["END"]})
        result = node.merge(extra_body=extra_body, options=existing)
        
        options = result[0]
        assert options["temperature"] == 0.7
        assert options["seed"] == 42
        assert options["num_ctx"] == 2048
        assert options["stop"] == ["END"]

    def test_merge_extra_body_overwrites_existing(self):
        """Test that extra_body can overwrite existing parameters."""
        node = OllamaOptionExtraBody()
        existing = {"temperature": 0.7}
        extra_body = json.dumps({"temperature": 0.9})
        result = node.merge(extra_body=extra_body, options=existing)
        
        options = result[0]
        # extra_body should overwrite existing temperature
        assert options["temperature"] == 0.9

    def test_merge_empty_extra_body(self):
        """Test merging empty JSON object."""
        node = OllamaOptionExtraBody()
        existing = {"seed": 42}
        result = node.merge(extra_body="{}", options=existing)
        
        options = result[0]
        # Should preserve existing options
        assert options["seed"] == 42


class TestOptionChaining:
    """Tests for chaining multiple option nodes together."""

    def test_chain_two_options(self):
        """Test chaining two option nodes."""
        temp_node = OllamaOptionTemperature()
        seed_node = OllamaOptionSeed()
        
        # First node
        result1 = temp_node.merge(temperature=0.7)
        options1 = result1[0]
        
        # Second node receives output from first
        result2 = seed_node.merge(seed=42, options=options1)
        options2 = result2[0]
        
        assert options2["temperature"] == 0.7
        assert options2["seed"] == 42

    def test_chain_three_options(self):
        """Test chaining three option nodes."""
        temp_node = OllamaOptionTemperature()
        seed_node = OllamaOptionSeed()
        max_tokens_node = OllamaOptionMaxTokens()
        
        # Chain them together
        result1 = temp_node.merge(temperature=0.8)
        result2 = seed_node.merge(seed=123, options=result1[0])
        result3 = max_tokens_node.merge(max_tokens=200, options=result2[0])
        
        final_options = result3[0]
        assert final_options["temperature"] == 0.8
        assert final_options["seed"] == 123
        assert final_options["num_predict"] == 200

    def test_chain_all_option_types(self):
        """Test chaining all option node types."""
        options = None
        
        # Chain all options together
        temp_result = OllamaOptionTemperature().merge(0.7, options)
        seed_result = OllamaOptionSeed().merge(42, temp_result[0])
        max_tokens_result = OllamaOptionMaxTokens().merge(150, seed_result[0])
        top_p_result = OllamaOptionTopP().merge(0.9, max_tokens_result[0])
        top_k_result = OllamaOptionTopK().merge(40, top_p_result[0])
        repeat_result = OllamaOptionRepeatPenalty().merge(1.1, top_k_result[0])
        extra_result = OllamaOptionExtraBody().merge(
            '{"num_ctx": 2048}', repeat_result[0]
        )
        
        final_options = extra_result[0]
        assert final_options["temperature"] == 0.7
        assert final_options["seed"] == 42
        assert final_options["num_predict"] == 150
        assert final_options["top_p"] == 0.9
        assert final_options["top_k"] == 40
        assert final_options["repeat_penalty"] == 1.1
        assert final_options["num_ctx"] == 2048

    def test_chain_with_duplicate_parameters(self):
        """Test that later options overwrite earlier ones."""
        temp_node1 = OllamaOptionTemperature()
        temp_node2 = OllamaOptionTemperature()
        
        result1 = temp_node1.merge(temperature=0.5)
        result2 = temp_node2.merge(temperature=0.9, options=result1[0])
        
        final_options = result2[0]
        # Later value should win
        assert final_options["temperature"] == 0.9


class TestNodeAttributes:
    """Test that all nodes have required attributes."""

    @pytest.mark.parametrize("node_class", [
        OllamaOptionTemperature,
        OllamaOptionSeed,
        OllamaOptionMaxTokens,
        OllamaOptionTopP,
        OllamaOptionTopK,
        OllamaOptionRepeatPenalty,
        OllamaOptionExtraBody,
    ])
    def test_node_has_required_attributes(self, node_class):
        """Test that each option node has required ComfyUI attributes."""
        assert hasattr(node_class, "INPUT_TYPES")
        assert hasattr(node_class, "RETURN_TYPES")
        assert hasattr(node_class, "RETURN_NAMES")
        assert hasattr(node_class, "FUNCTION")
        assert hasattr(node_class, "CATEGORY")
        
        # Check values
        assert node_class.RETURN_TYPES == ("OLLAMA_OPTIONS",)
        assert node_class.RETURN_NAMES == ("options",)
        assert node_class.FUNCTION == "merge"
        assert node_class.CATEGORY == "Ollama/Options"

    @pytest.mark.parametrize("node_class", [
        OllamaOptionTemperature,
        OllamaOptionSeed,
        OllamaOptionMaxTokens,
        OllamaOptionTopP,
        OllamaOptionTopK,
        OllamaOptionRepeatPenalty,
        OllamaOptionExtraBody,
    ])
    def test_node_can_be_instantiated(self, node_class):
        """Test that each node can be instantiated."""
        node = node_class()
        assert node is not None
        assert hasattr(node, "merge")
