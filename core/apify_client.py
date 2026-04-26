from __future__ import annotations

import asyncio
import logging
from functools import partial
from typing import Any

from apify_client import ApifyClient
from apify_client.consts import ActorJobStatus
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class ApifyClientWrapper:
    """Wraps the synchronous Apify SDK and exposes an async interface."""

    def __init__(self, api_token: str, proxy_rotation_enabled: bool = True) -> None:
        self._api_token = api_token
        self._proxy_rotation_enabled = proxy_rotation_enabled
        self._client = ApifyClient(token=api_token)

    async def run_actor(
        self,
        actor_id: str,
        run_input: dict,
        timeout_secs: int = 120,
    ) -> list[dict]:
        """Run an Apify actor and return dataset items.

        The underlying SDK is synchronous, so the blocking call is offloaded to
        a thread-pool executor to avoid stalling the event loop. Retries up to
        3 times with exponential back-off.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            partial(self._sync_run_actor, actor_id, run_input, timeout_secs),
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def _sync_run_actor(
        self,
        actor_id: str,
        run_input: dict[str, Any],
        timeout_secs: int,
    ) -> list[dict]:
        """Blocking implementation — called from run_actor via run_in_executor."""
        try:
            run = self._client.actor(actor_id).call(
                run_input=run_input,
                timeout_secs=timeout_secs,
            )
        except Exception as exc:
            raise RuntimeError(f"Actor '{actor_id}' call failed: {exc}") from exc

        if run is None:
            raise RuntimeError(f"Actor '{actor_id}' returned no run object.")

        status = run.get("status")
        if status not in (ActorJobStatus.SUCCEEDED, "SUCCEEDED"):
            raise RuntimeError(
                f"Actor '{actor_id}' finished with non-success status: {status}"
            )

        dataset_id = run.get("defaultDatasetId")
        if not dataset_id:
            raise RuntimeError(f"Actor '{actor_id}' run produced no dataset id.")

        items: list[dict] = list(self._client.dataset(dataset_id).iterate_items())
        logger.info("Actor '%s' completed — %d items retrieved.", actor_id, len(items))
        return items

    def _build_proxy_config(self) -> dict:
        if self._proxy_rotation_enabled:
            return {"useApifyProxy": True, "apifyProxyGroups": ["RESIDENTIAL"]}
        return {}
