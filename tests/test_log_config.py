"""Tests for logging configuration."""

import pytest
from comfyui_ollama_model_manager.log_config import (
    get_logger,
    set_request_id,
    scrub_secrets,
)


def test_get_logger():
    """Test getting a logger instance."""
    logger = get_logger()
    assert logger is not None
    assert hasattr(logger, "info")
    assert hasattr(logger, "error")
    assert hasattr(logger, "debug")


def test_set_request_id():
    """Test setting correlation ID."""
    test_id = "test-123"
    set_request_id(test_id)
    # If this doesn't raise, it works
    assert True


def test_scrub_secrets():
    """Test secret scrubbing from log messages."""
    # Test with Bearer token
    text = "Authorization: Bearer abc123def456ghi789jkl012mno345pqr678stu901"
    scrubbed = scrub_secrets(text)
    assert "Bearer <redacted>" in scrubbed
    assert "abc123def456ghi789jkl012mno345pqr678stu901" not in scrubbed
    
    # Test with no secrets
    text = "This is a normal log message"
    scrubbed = scrub_secrets(text)
    assert scrubbed == text


def test_logger_can_log_messages():
    """Test that logger can actually log messages without errors."""
    logger = get_logger()
    
    # These should not raise exceptions
    logger.info("Test info message")
    logger.debug("Test debug message")
    logger.warning("Test warning message")
    
    # Test with structured data
    logger.info("Test with data", extra={"key": "value"})
