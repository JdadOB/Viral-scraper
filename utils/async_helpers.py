from __future__ import annotations

import asyncio
from typing import Any, Coroutine, TypeVar

T = TypeVar("T")


async def gather_with_concurrency(n: int, *coros: Coroutine[Any, Any, T]) -> list[T]:
    """Run coroutines concurrently, but cap in-flight coroutines to *n* at a time.

    Args:
        n: Maximum number of coroutines to run concurrently.
        *coros: Coroutines to execute.

    Returns:
        A list of results in the same order as the input coroutines.
    """
    semaphore = asyncio.Semaphore(n)

    async def _run(coro: Coroutine[Any, Any, T]) -> T:
        async with semaphore:
            return await coro

    return list(await asyncio.gather(*(_run(c) for c in coros)))


def run_async(coro: Coroutine[Any, Any, T]) -> T:
    """Run an async coroutine from a synchronous context.

    Uses the running event loop if one already exists (e.g. inside Jupyter or
    Streamlit), otherwise creates a fresh one via asyncio.run().

    Args:
        coro: The coroutine to execute.

    Returns:
        The return value of the coroutine.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop is not None and loop.is_running():
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(asyncio.run, coro)
            return future.result()

    return asyncio.run(coro)
