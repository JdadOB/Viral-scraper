from __future__ import annotations

import logging
import re
from datetime import datetime
from typing import Optional

from config.settings import AppSettings
from core.apify_client import ApifyClientWrapper
from core.data_models import Platform, ScraperResult, VideoItem

logger = logging.getLogger(__name__)

_HASHTAG_RE = re.compile(r"#(\w+)")


def _is_reel(raw: dict) -> bool:
    """Return True if the item is a video or reel (not a static photo)."""
    if raw.get("isVideo") is True:
        return True
    media_type = str(raw.get("type") or raw.get("mediaType") or "").lower()
    if "video" in media_type or "reel" in media_type:
        return True
    if raw.get("videoUrl"):
        return True
    if int(raw.get("videoPlayCount") or raw.get("videoViewCount") or 0) > 0:
        return True
    return False


class InstagramScraper:
    """Scrapes Instagram Reels via the Apify apify/instagram-hashtag-scraper actor."""

    def __init__(self, client: ApifyClientWrapper, settings: AppSettings) -> None:
        self._client = client
        self._settings = settings

    def _build_input(self, hashtag: str, limit: int) -> dict:
        return {
            "hashtags": [hashtag.lstrip("#")],
            "resultsLimit": limit,
            "addParentData": True,   # needed to get ownerFollowersCount
            "proxy": self._client._build_proxy_config(),
        }

    async def scrape_hashtag(
        self,
        hashtag: str,
        max_results: Optional[int] = None,
    ) -> ScraperResult:
        limit = max_results if max_results is not None else self._settings.max_results_per_query
        clean_hashtag = hashtag.lstrip("#")
        run_input = self._build_input(clean_hashtag, limit)

        try:
            raw_items = await self._client.run_actor(
                actor_id=self._settings.instagram_actor_id,
                run_input=run_input,
            )
            video_items = [self._map_item(r) for r in raw_items if _is_reel(r)]
            logger.info(
                "Instagram hashtag '#%s': %d raw items, %d reels kept.",
                clean_hashtag, len(raw_items), len(video_items),
            )
            return ScraperResult(
                platform=Platform.INSTAGRAM,
                query=f"#{clean_hashtag}",
                items=video_items,
                total_count=len(video_items),
                success=True,
            )
        except Exception as exc:
            logger.error("Instagram hashtag scrape failed for '%s': %s", hashtag, exc)
            return ScraperResult(
                platform=Platform.INSTAGRAM,
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
        # The hashtag actor works best with hashtag-style queries
        return await self.scrape_hashtag(keyword, max_results=max_results)

    def _map_item(self, raw: dict) -> VideoItem:
        caption: str = str(raw.get("caption") or raw.get("alt") or "")
        hashtags: list[str] = _HASHTAG_RE.findall(caption)

        # Sound info
        music_info = raw.get("musicInfo") or {}
        sound_name: str = str(
            music_info.get("songName")
            or music_info.get("artistName")
            or raw.get("musicName")
            or raw.get("audioTitle")
            or ""
        )

        # Timestamp
        posted_at: Optional[datetime] = None
        timestamp = raw.get("timestamp") or raw.get("takenAtTimestamp")
        if timestamp is not None:
            if isinstance(timestamp, (int, float)):
                try:
                    posted_at = datetime.utcfromtimestamp(int(timestamp))
                except (ValueError, OSError, OverflowError):
                    posted_at = None
            elif isinstance(timestamp, str):
                for fmt in (
                    "%Y-%m-%dT%H:%M:%S.%fZ",
                    "%Y-%m-%dT%H:%M:%SZ",
                    "%Y-%m-%d %H:%M:%S",
                    "%Y-%m-%dT%H:%M:%S+00:00",
                ):
                    try:
                        posted_at = datetime.strptime(timestamp, fmt)
                        break
                    except ValueError:
                        continue

        play_count = int(raw.get("videoPlayCount") or raw.get("playCount") or 0)
        view_count = int(raw.get("videoViewCount") or raw.get("viewCount") or play_count)

        follower_count = int(
            raw.get("ownerFollowersCount")
            or raw.get("followersCount")
            or raw.get("followers")
            or 0
        )

        shortcode = raw.get("shortCode") or raw.get("shortcode") or ""
        url = str(
            raw.get("url")
            or (f"https://www.instagram.com/reel/{shortcode}/" if shortcode else "")
            or ""
        )

        return VideoItem(
            id=str(raw.get("id") or shortcode or ""),
            platform=Platform.INSTAGRAM,
            url=url,
            author=str(raw.get("ownerUsername") or raw.get("username") or ""),
            description=caption,
            thumbnail_url=str(raw.get("thumbnailUrl") or raw.get("displayUrl") or ""),
            play_count=play_count,
            like_count=int(raw.get("likesCount") or raw.get("likeCount") or 0),
            comment_count=int(raw.get("commentsCount") or raw.get("commentCount") or 0),
            share_count=0,
            save_count=0,
            view_count=view_count,
            follower_count=follower_count,
            duration_seconds=float(raw.get("videoDuration") or raw.get("duration") or 0.0),
            hashtags=hashtags,
            sound_name=sound_name,
            sound_duration_days=0,
            posted_at=posted_at,
            raw_data=raw,
        )
