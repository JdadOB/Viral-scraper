from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from config.settings import AppSettings
from core.apify_client import ApifyClientWrapper
from core.data_models import Platform, ScraperResult, VideoItem

logger = logging.getLogger(__name__)


class TikTokScraper:
    """Scrapes TikTok content via the Apify clockworks/tiktok-scraper actor."""

    def __init__(self, client: ApifyClientWrapper, settings: AppSettings) -> None:
        self._client = client
        self._settings = settings

    async def scrape_hashtag(
        self,
        hashtag: str,
        max_results: Optional[int] = None,
    ) -> ScraperResult:
        """Scrape TikTok videos for a given hashtag."""
        limit = max_results if max_results is not None else self._settings.max_results_per_query
        clean_hashtag = hashtag.lstrip("#")

        run_input: dict = {
            "hashtags": [clean_hashtag],
            "resultsPerPage": limit,
            "maxResults": limit,
            "shouldDownloadVideos": False,
            "shouldDownloadCovers": False,
            "proxyConfiguration": self._client._build_proxy_config(),
        }

        try:
            raw_items = await self._client.run_actor(
                actor_id=self._settings.tiktok_actor_id,
                run_input=run_input,
            )
            video_items = [self._map_item(raw) for raw in raw_items]
            return ScraperResult(
                platform=Platform.TIKTOK,
                query=f"#{clean_hashtag}",
                items=video_items,
                total_count=len(video_items),
                success=True,
            )
        except Exception as exc:
            logger.error("TikTok hashtag scrape failed for '%s': %s", hashtag, exc)
            return ScraperResult(
                platform=Platform.TIKTOK,
                query=f"#{clean_hashtag}",
                items=[],
                total_count=0,
                success=False,
                error_message=str(exc),
            )

    async def scrape_keyword(
        self,
        keyword: str,
        max_results: Optional[int] = None,
    ) -> ScraperResult:
        """Scrape TikTok videos for a given keyword search."""
        limit = max_results if max_results is not None else self._settings.max_results_per_query

        run_input: dict = {
            "searchQueries": [keyword],
            "resultsPerPage": limit,
            "maxResults": limit,
            "shouldDownloadVideos": False,
            "shouldDownloadCovers": False,
            "proxyConfiguration": self._client._build_proxy_config(),
        }

        try:
            raw_items = await self._client.run_actor(
                actor_id=self._settings.tiktok_actor_id,
                run_input=run_input,
            )
            video_items = [self._map_item(raw) for raw in raw_items]
            return ScraperResult(
                platform=Platform.TIKTOK,
                query=keyword,
                items=video_items,
                total_count=len(video_items),
                success=True,
            )
        except Exception as exc:
            logger.error("TikTok keyword scrape failed for '%s': %s", keyword, exc)
            return ScraperResult(
                platform=Platform.TIKTOK,
                query=keyword,
                items=[],
                total_count=0,
                success=False,
                error_message=str(exc),
            )

    def _map_item(self, raw: dict) -> VideoItem:
        """Map a raw TikTok API response dict to a VideoItem."""
        author_meta = raw.get("authorMeta") or {}
        music_meta = raw.get("musicMeta") or {}
        video_meta = raw.get("videoMeta") or {}

        raw_hashtags = raw.get("hashtags") or []
        hashtags: list[str] = []
        for tag in raw_hashtags:
            if isinstance(tag, dict):
                name = tag.get("name", "")
                if name:
                    hashtags.append(name)
            elif isinstance(tag, str) and tag:
                hashtags.append(tag)

        posted_at: Optional[datetime] = None
        create_time = raw.get("createTime")
        if create_time is not None:
            try:
                posted_at = datetime.utcfromtimestamp(int(create_time))
            except (ValueError, OSError, OverflowError):
                posted_at = None

        sound_duration_raw = music_meta.get("duration") or music_meta.get("musicDuration") or 0
        try:
            sound_duration_days = int(sound_duration_raw) // 86400
        except (TypeError, ValueError):
            sound_duration_days = 0

        follower_count = int(
            author_meta.get("fans") or author_meta.get("followers") or
            author_meta.get("followerCount") or 0
        )

        return VideoItem(
            id=str(raw.get("id") or ""),
            platform=Platform.TIKTOK,
            url=str(raw.get("webVideoUrl") or raw.get("url") or ""),
            author=str(author_meta.get("name") or raw.get("authorName") or ""),
            description=str(raw.get("text") or raw.get("description") or ""),
            thumbnail_url=str(raw.get("covers", [None])[0] if raw.get("covers") else video_meta.get("coverUrl") or ""),
            play_count=int(raw.get("playCount") or 0),
            like_count=int(raw.get("diggCount") or raw.get("likeCount") or 0),
            comment_count=int(raw.get("commentCount") or 0),
            share_count=int(raw.get("shareCount") or 0),
            save_count=int(raw.get("collectCount") or raw.get("saveCount") or 0),
            view_count=int(raw.get("playCount") or 0),
            follower_count=follower_count,
            duration_seconds=float(video_meta.get("duration") or raw.get("videoMeta", {}).get("duration") or 0.0),
            hashtags=hashtags,
            sound_name=str(music_meta.get("musicName") or music_meta.get("soundName") or ""),
            sound_duration_days=sound_duration_days,
            posted_at=posted_at,
            raw_data=raw,
        )
