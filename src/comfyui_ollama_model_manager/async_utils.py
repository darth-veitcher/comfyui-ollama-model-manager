"""Utilities for running async code from sync contexts."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Coroutine, TypeVar

from .log_config import get_logger

log = get_logger()

T = TypeVar("T")

# Thread pool for running async code when event loop is already running
_executor = ThreadPoolExecutor(max_workers=4)


def run_async(coro: Coroutine[None, None, T]) -> T:
    """
    Run async coroutine from sync context.

    When called from within an existing event loop (like ComfyUI's),
    runs the coroutine in a separate thread with its own event loop.
    Otherwise, creates a new event loop.

    Args:
        coro: Coroutine to execute

    Returns:
        Result from the coroutine
    """
    try:
        asyncio.get_running_loop()
        log.debug("Existing event loop detected, running in thread pool")
        # We're inside an event loop, run in a separate thread
        future = _executor.submit(asyncio.run, coro)
        return future.result()
    except RuntimeError:
        log.debug("No event loop found, creating new one")
        # No event loop running, safe to use asyncio.run
        return asyncio.run(coro)
