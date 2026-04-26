from __future__ import annotations

import logging
from typing import Any

from apify_client import ApifyClient
from apify_client.consts import ActorJobStatus
from tenacity import retry, stop_after_attempt, wait_exponential

from config.settings import settings

logger = logging.getLogger(__name__)


class ApifyClientWrapper:
    """Async-friendly wrapper around the Apify Python SDK client."""

    def __init__(self, api_token: str) -> None:
        self._api_token = api_token
        self._client = ApifyClient(token=api_token)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def run_actor(
        self,
        actor_id: str,
        run_input: dict,
        timeout_secs: int = 120,
    ) -> list[dict]:
        """Run an Apify actor and return the dataset items.

        Retries up to 3 times with exponential back-off on failure.
        """
        try:
            actor_client = self._client.actor(actor_id)
            run = actor_client.call(
                run_input=run_input,
                timeout_secs=timeout_secs,
            )

            if run is None:
                raise RuntimeError(
                    f"Actor '{actor_id}' returned no run object."
                )

            status = run.get("status")
            if status not in (ActorJobStatus.SUCCEEDED, "SUCCEEDED"):
                raise RuntimeError(
                    f"Actor '{actor_id}' finished with non-success status: {status}"
                )

            dataset_id = run.get("defaultDatasetId")
            if not dataset_id:
                raise RuntimeError(
                    f"Actor '{actor_id}' run produced no dataset id."
                )

            items: list[dict] = []
            for item in self._client.dataset(dataset_id).iterate_items():
                items.append(item)

            logger.info(
                "Actor '%s' completed successfully. Retrieved %d items.",
                actor_id,
                len(items),
            )
            return items

        except RuntimeError:
            raise
        except Exception as exc:
            raise RuntimeError(
                f"Actor '{actor_id}' run failed: {exc}"
            ) from exc

    def _build_proxy_config(self) -> dict:
        """Return an Apify proxy configuration dict based on current settings."""
        if settings.proxy_rotation_enabled:
            return {
                "useApifyProxy": True,
                "apifyProxyGroups": ["RESIDENTIAL"],
            }
        return {}
