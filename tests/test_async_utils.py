"""Tests for async utilities module."""

import asyncio

import pytest

from comfyui_ollama_model_manager.async_utils import run_async


async def sample_coroutine(value):
    """A simple coroutine for testing."""
    await asyncio.sleep(0.001)
    return value * 2


def test_run_async_basic():
    """Test running a simple coroutine."""
    result = run_async(sample_coroutine(5))
    assert result == 10


def test_run_async_with_exception():
    """Test that exceptions are propagated correctly."""

    async def failing_coroutine():
        await asyncio.sleep(0.001)
        raise ValueError("Test error")

    with pytest.raises(ValueError, match="Test error"):
        run_async(failing_coroutine())


def test_run_async_returns_value():
    """Test that return values are passed through correctly."""

    async def return_dict():
        return {"status": "success", "data": [1, 2, 3]}

    result = run_async(return_dict())
    assert result == {"status": "success", "data": [1, 2, 3]}
