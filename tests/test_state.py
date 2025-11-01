"""Tests for state management module."""

import pytest
from comfyui_ollama_model_manager.state import (
    get_endpoint,
    get_models,
    set_models,
)


def test_initial_state():
    """Test the initial state of the model cache."""
    endpoint = get_endpoint()
    assert endpoint == "http://localhost:11434"


def test_set_and_get_models(mock_endpoint, sample_models):
    """Test setting and getting models from cache."""
    set_models(mock_endpoint, sample_models)
    
    assert get_endpoint() == mock_endpoint
    assert get_models() == sample_models


def test_get_models_returns_copy(mock_endpoint, sample_models):
    """Ensure get_models returns a copy, not the original list."""
    set_models(mock_endpoint, sample_models)
    
    models1 = get_models()
    models2 = get_models()
    
    # Should be equal but not the same object
    assert models1 == models2
    assert models1 is not models2


def test_empty_models_list(mock_endpoint):
    """Test setting an empty models list."""
    set_models(mock_endpoint, [])
    
    assert get_models() == []
    assert get_endpoint() == mock_endpoint
