from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    apify_api_token: str = Field(..., env="APIFY_API_TOKEN")
    tiktok_actor_id: str = Field(default="clockworks/tiktok-scraper", env="TIKTOK_ACTOR_ID")
    instagram_actor_id: str = Field(default="apify/instagram-hashtag-scraper", env="INSTAGRAM_ACTOR_ID")
    max_results_per_query: int = Field(default=50, env="MAX_RESULTS_PER_QUERY")
    proxy_rotation_enabled: bool = Field(default=True, env="PROXY_ROTATION_ENABLED")
    cache_ttl_seconds: int = Field(default=300, env="CACHE_TTL_SECONDS")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """Return a cached AppSettings instance. Raises at call time, not import time."""
    return AppSettings()
