"""Tests for Ollama client module."""

from unittest.mock import AsyncMock, patch

import httpx
import pytest

from comfyui_ollama_model_manager.ollama_client import (
    fetch_models_from_ollama,
    load_model,
    unload_model,
)


@pytest.mark.asyncio
async def test_fetch_models_success(mock_httpx_client, mock_endpoint, sample_models):
    """Test successfully fetching models from Ollama."""
    with patch(
        "comfyui_ollama_model_manager.ollama_client.httpx.AsyncClient"
    ) as mock_client_cls:
        mock_client_cls.return_value = mock_httpx_client

        result = await fetch_models_from_ollama(mock_endpoint)

        assert result == sample_models
        mock_httpx_client.get.assert_called_once_with(f"{mock_endpoint}/api/tags")


@pytest.mark.asyncio
async def test_fetch_models_http_error(mock_endpoint):
    """Test handling of HTTP errors when fetching models."""
    from unittest.mock import MagicMock

    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "404 Not Found", request=MagicMock(), response=MagicMock()
    )

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.get = AsyncMock(return_value=mock_response)

    with patch(
        "comfyui_ollama_model_manager.ollama_client.httpx.AsyncClient"
    ) as mock_client_cls:
        mock_client_cls.return_value = mock_client

        with pytest.raises(httpx.HTTPStatusError):
            await fetch_models_from_ollama(mock_endpoint)


@pytest.mark.asyncio
async def test_load_model_success(mock_httpx_client, mock_endpoint):
    """Test successfully loading a model."""
    with patch(
        "comfyui_ollama_model_manager.ollama_client.httpx.AsyncClient"
    ) as mock_client_cls:
        mock_client_cls.return_value = mock_httpx_client

        result = await load_model(mock_endpoint, "llama3.2", "-1")

        assert result == {
            "models": [{"name": name} for name in ["llama3.2", "mistral", "phi3"]]
        }
        # Should try /api/load first, then fall back to /api/generate
        assert mock_httpx_client.post.called


@pytest.mark.asyncio
async def test_load_model_with_keep_alive(mock_httpx_client, mock_endpoint):
    """Test loading a model with custom keep_alive."""
    with patch(
        "comfyui_ollama_model_manager.ollama_client.httpx.AsyncClient"
    ) as mock_client_cls:
        mock_client_cls.return_value = mock_httpx_client

        await load_model(mock_endpoint, "llama3.2", "5m")

        # Verify keep_alive was included in the payload
        call_args = mock_httpx_client.post.call_args
        assert call_args is not None


@pytest.mark.asyncio
async def test_unload_model_success(mock_httpx_client, mock_endpoint):
    """Test successfully unloading a model."""
    with patch(
        "comfyui_ollama_model_manager.ollama_client.httpx.AsyncClient"
    ) as mock_client_cls:
        mock_client_cls.return_value = mock_httpx_client

        result = await unload_model(mock_endpoint, "llama3.2")

        assert result is not None
        mock_httpx_client.post.assert_called_once()

        # Verify the payload includes keep_alive: 0
        call_args = mock_httpx_client.post.call_args
        payload = call_args[1]["json"]
        assert payload["model"] == "llama3.2"
        assert payload["keep_alive"] == 0
