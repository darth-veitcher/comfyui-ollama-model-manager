"""Pytest configuration and fixtures."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from comfyui_ollama_model_manager.state import set_models


def pytest_configure(config):
    """
    Configure pytest with custom warning filters.

    This runs before tests and uses pytest's configuration API to add filters.
    Suppresses RuntimeWarnings from unittest.mock internals which are false
    positives from mock's handling of async functions.
    """
    # Use pytest's addinivalue_line to add filters
    config.addinivalue_line(
        "filterwarnings",
        "ignore::RuntimeWarning:unittest.mock",
    )
    config.addinivalue_line(
        "filterwarnings",
        "ignore:coroutine.*was never awaited:RuntimeWarning",
    )
    config.addinivalue_line(
        "filterwarnings",
        "ignore::RuntimeWarning:_pytest.unraisableexception",
    )


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
