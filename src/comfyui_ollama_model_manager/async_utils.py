"""Utilities for running async code from sync contexts."""

import asyncio
from typing import Coroutine, TypeVar

from .log_config import get_logger

log = get_logger()

T = TypeVar("T")


def run_async(coro: Coroutine[None, None, T]) -> T:
    """
    Run async coroutine from sync context (ComfyUI calls nodes synchronously).

    Args:
        coro: Coroutine to execute

    Returns:
        Result from the coroutine
    """
    try:
        loop = asyncio.get_running_loop()
        log.debug("Running coroutine in existing event loop")
    except RuntimeError:
        log.debug("Creating new event loop to run coroutine")
        return asyncio.run(coro)
    else:
        return loop.run_until_complete(coro)
