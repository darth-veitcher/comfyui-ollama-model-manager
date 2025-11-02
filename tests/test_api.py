"""Tests for the ComfyUI API routes."""

from comfyui_ollama_model_manager.api import setup_api_routes


def test_setup_api_routes_without_comfyui():
    """Test that setup_api_routes doesn't crash when ComfyUI server is not available."""
    # This should not raise an exception even though server module is not available
    setup_api_routes()
    # If we got here, the function handled the ImportError gracefully
    assert True


def test_api_imports():
    """Test that API module can be imported."""
    from comfyui_ollama_model_manager import api
    
    assert hasattr(api, "setup_api_routes")
    assert callable(api.setup_api_routes)
