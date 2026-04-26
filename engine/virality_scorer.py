from __future__ import annotations

from datetime import datetime
from math import log10

from core.data_models import VideoItem


class ViralityScorer:
    """Scores VideoItems on a 0–100 virality scale.

    Primary signal: view-to-follower ratio — a video is viral when it
    reaches far beyond the creator's existing audience.
    Secondary signals: engagement velocity and engagement rate vs views.
    """

    # Weights — must sum to 1.0
    W_VIEW_FOLLOWER = 0.55
    W_ENGAGEMENT_VELOCITY = 0.25
    W_ENGAGEMENT_RATE = 0.20

    # Engagement velocity thresholds (total actions per hour → score 100)
    TOTAL_ENGAGEMENT_THRESHOLD = 2_000  # likes+comments+shares/hr

    def score(self, item: VideoItem) -> float:
        """Return a virality score in [0, 100]."""
        vf = self._view_follower_score(item)
        vel = self._engagement_velocity_score(item)
        rate = self._engagement_rate_score(item)
        raw = vf * self.W_VIEW_FOLLOWER + vel * self.W_ENGAGEMENT_VELOCITY + rate * self.W_ENGAGEMENT_RATE
        return round(min(max(raw, 0.0), 100.0), 4)

    def score_batch(self, items: list[VideoItem]) -> list[VideoItem]:
        """Score every item and return sorted descending by virality_score."""
        for item in items:
            item.virality_score = self.score(item)
        return sorted(items, key=lambda x: x.virality_score, reverse=True)

    # ------------------------------------------------------------------
    # Sub-scores
    # ------------------------------------------------------------------

    def _view_follower_score(self, item: VideoItem) -> float:
        """55% weight — how far the video punched above the creator's reach.

        Uses a log10 scale so that small accounts going mega-viral score
        just as high as large accounts going relatively viral:
          ratio  1x  →  score   0   (performed as expected)
          ratio  5x  →  score  35
          ratio 10x  →  score  50
          ratio 50x  →  score  85
          ratio 100x →  score 100
        """
        views = item.view_count or item.play_count
        followers = item.follower_count

        if followers <= 0:
            # No follower data — fall back to absolute view count signal
            # 1M views ≈ score 70, 10M views ≈ score 100
            if views <= 0:
                return 0.0
            return min(log10(max(views, 1)) / 7 * 100, 100.0)

        ratio = views / followers
        if ratio <= 1.0:
            return 0.0
        # log10(ratio) / log10(100) * 100  →  100x = score 100
        return min(log10(ratio) / 2.0 * 100, 100.0)

    def _engagement_velocity_score(self, item: VideoItem) -> float:
        """25% weight — total engagement actions per hour since posting."""
        if item.posted_at is not None:
            posted = item.posted_at
            now = datetime.utcnow()
            if posted.tzinfo is not None:
                from datetime import timezone
                now = datetime.now(timezone.utc)
            hours = max((now - posted).total_seconds() / 3600.0, 1.0)
        else:
            hours = 24.0

        total_engagement = item.like_count + item.comment_count + item.share_count
        per_hour = total_engagement / hours
        return min(per_hour / self.TOTAL_ENGAGEMENT_THRESHOLD, 1.0) * 100.0

    def _engagement_rate_score(self, item: VideoItem) -> float:
        """20% weight — (likes + comments + shares) / views.

          < 1%  →  low
            3%  →  good  (score ~60)
            5%  →  great (score ~100)
           10%+ →  capped at 100
        """
        views = max(item.view_count or item.play_count, 1)
        total_engagement = item.like_count + item.comment_count + item.share_count
        rate = total_engagement / views
        return min(rate / 0.05, 1.0) * 100.0
