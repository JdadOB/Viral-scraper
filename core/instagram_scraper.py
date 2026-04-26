from __future__ import annotations

import logging
import re
from datetime import datetime, timedelta
from typing import Optional

from config.settings import AppSettings
from core.apify_client import ApifyClientWrapper
from core.data_models import Platform, ScraperResult, VideoItem

logger = logging.getLogger(__name__)

_HASHTAG_RE = re.compile(r"#(\w+)")


class InstagramScraper:
    """Scrapes Instagram Reels via the Apify apify/instagram-reel-scraper actor."""

    def __init__(self, client: ApifyClientWrapper, settings: AppSettings) -> None:
        self._client = client
        self._settings = settings

    def _build_input(self, hashtag: str, limit: int) -> dict:
        return {
            "hashtags": [hashtag.lstrip("#")],
            "resultsLimit": limit,
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
            video_items = [self._map_item(r) for r in raw_items]
            logger.info(
                "Instagram hashtag '#%s': %d reels fetched.",
                clean_hashtag, len(video_items),
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
        # The Reels actor works with hashtags; treat keyword as a hashtag search
        return await self.scrape_hashtag(keyword, max_results=max_results)

    def _map_item(self, raw: dict) -> VideoItem:
        # apify/instagram-reel-scraper field names
        caption: str = str(raw.get("caption") or raw.get("text") or "")
        hashtags: list[str] = _HASHTAG_RE.findall(caption)

        # Sound / music info
        music_info = raw.get("musicInfo") or raw.get("music") or {}
        sound_name: str = str(
            music_info.get("title")
            or music_info.get("artist")
            or music_info.get("songName")
            or raw.get("musicTitle")
            or raw.get("audioTitle")
            or ""
        )

        # Timestamp — the actor emits ISO strings or unix timestamps
        posted_at: Optional[datetime] = None
        timestamp = (
            raw.get("timestamp")
            or raw.get("taken_at_timestamp")
            or raw.get("takenAtTimestamp")
            or raw.get("created_time")
        )
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

        # Play / view counts
        play_count = int(
            raw.get("videoPlayCount")
            or raw.get("playCount")
            or raw.get("video_view_count")
            or 0
        )
        view_count = int(
            raw.get("videoViewCount")
            or raw.get("viewCount")
            or raw.get("playsCount")
            or play_count
        )

        # Follower count — owner object or top-level keys
        owner = raw.get("owner") or raw.get("user") or {}
        follower_count = int(
            raw.get("followersCount")
            or raw.get("ownerFollowersCount")
            or owner.get("followersCount")
            or owner.get("followers_count")
            or raw.get("followers")
            or 0
        )

        # Author username
        author = str(
            raw.get("ownerUsername")
            or raw.get("username")
            or owner.get("username")
            or raw.get("ownerId")
            or ""
        )

        # Thumbnail
        thumbnail_url = str(
            raw.get("thumbnailUrl")
            or raw.get("displayUrl")
            or raw.get("thumbnail")
            or raw.get("previewUrl")
            or ""
        )

        # Canonical URL
        shortcode = raw.get("shortCode") or raw.get("shortcode") or ""
        url = str(
            raw.get("url")
            or (f"https://www.instagram.com/reel/{shortcode}/" if shortcode else "")
            or raw.get("link")
            or ""
        )

        return VideoItem(
            id=str(raw.get("id") or shortcode or ""),
            platform=Platform.INSTAGRAM,
            url=url,
            author=author,
            description=caption,
            thumbnail_url=thumbnail_url,
            play_count=play_count,
            like_count=int(raw.get("likesCount") or raw.get("likeCount") or raw.get("likes_count") or 0),
            comment_count=int(raw.get("commentsCount") or raw.get("commentCount") or raw.get("comments_count") or 0),
            share_count=int(raw.get("sharesCount") or raw.get("shareCount") or 0),
            save_count=int(raw.get("savesCount") or raw.get("saveCount") or 0),
            view_count=view_count,
            follower_count=follower_count,
            duration_seconds=float(raw.get("videoDuration") or raw.get("duration") or 0.0),
            hashtags=hashtags,
            sound_name=sound_name,
            sound_duration_days=0,
            posted_at=posted_at,
            raw_data=raw,
        )
