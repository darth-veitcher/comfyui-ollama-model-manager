"""Pytest configuration and fixtures."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from comfyui_ollama_model_manager.state import set_models


@pytest.fixture
def mock_endpoint():
    """Provide a mock Ollama endpoint URL."""
    return "http://localhost:11434"


@pytest.fixture
def sample_models():
    """Provide sample model names."""
    return ["llama3.2", "mistral", "phi3"]


@pytest.fixture
def populated_cache(mock_endpoint, sample_models):
    """Set up the model cache with sample data."""
    set_models(mock_endpoint, sample_models)
    yield
    # Cleanup: reset to empty
    set_models(mock_endpoint, [])


@pytest.fixture
def mock_httpx_client(sample_models):
    """Mock httpx.AsyncClient for testing API calls."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "models": [{"name": name} for name in sample_models]
    }
    mock_response.raise_for_status = MagicMock()
    
    # Create an AsyncMock for the client itself
    mock_client = AsyncMock()
    # Mock the context manager methods
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    # Mock the HTTP methods
    mock_client.get.return_value = mock_response
    mock_client.post.return_value = mock_response
    
    return mock_client
