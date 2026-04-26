from datetime import datetime
from math import log
import numpy as np

from core.data_models import VideoItem


class ViralityScorer:
    """Scores VideoItems on a 0–100 virality scale using four weighted sub-scores."""

    # Normalisation thresholds (per-hour rates that map to 100)
    LIKES_THRESHOLD = 10_000   # likes/hr → 100
    VIEWS_THRESHOLD = 100_000  # views/hr → 100
    COMMENTS_THRESHOLD = 500   # comments/hr → 100

    # Sub-score weights (must sum to 1.0)
    W_VELOCITY = 0.35
    W_SAVE_VIEW = 0.25
    W_SOUND = 0.20
    W_DIVERSITY = 0.20

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def score(self, item: VideoItem) -> float:
        """Return a virality score in [0, 100] for a single VideoItem."""
        velocity = self._engagement_velocity_score(item)
        save_view = self._save_view_ratio_score(item)
        sound = self._sound_trend_score(item)
        diversity = self._engagement_diversity_score(item)

        raw = (
            velocity * self.W_VELOCITY
            + save_view * self.W_SAVE_VIEW
            + sound * self.W_SOUND
            + diversity * self.W_DIVERSITY
        )
        return round(min(max(raw, 0.0), 100.0), 4)

    def score_batch(self, items: list[VideoItem]) -> list[VideoItem]:
        """Score every item in *items*, set virality_score, and return sorted descending."""
        for item in items:
            item.virality_score = self.score(item)
        return sorted(items, key=lambda x: x.virality_score, reverse=True)

    # ------------------------------------------------------------------ #
    # Sub-scores                                                           #
    # ------------------------------------------------------------------ #

    def _engagement_velocity_score(self, item: VideoItem) -> float:
        """35 % weight — rate of likes, views, and comments per hour."""
        if item.posted_at is not None:
            now = datetime.utcnow()
            # Make both naive for subtraction if needed
            posted = item.posted_at
            if posted.tzinfo is not None:
                from datetime import timezone
                now = datetime.now(timezone.utc)
            hours = (now - posted).total_seconds() / 3600.0
        else:
            hours = 24.0

        hours = max(hours, 1.0)

        likes_per_hr = item.like_count / hours
        views_per_hr = item.view_count / hours
        comments_per_hr = item.comment_count / hours

        likes_norm = min(likes_per_hr / self.LIKES_THRESHOLD, 1.0) * 100.0
        views_norm = min(views_per_hr / self.VIEWS_THRESHOLD, 1.0) * 100.0
        comments_norm = min(comments_per_hr / self.COMMENTS_THRESHOLD, 1.0) * 100.0

        return likes_norm * 0.4 + views_norm * 0.4 + comments_norm * 0.2

    def _save_view_ratio_score(self, item: VideoItem) -> float:
        """25 % weight — save-to-view ratio (5 % = perfect score)."""
        ratio = item.save_count / max(item.view_count, 1)
        return min(ratio / 0.05, 1.0) * 100.0

    def _sound_trend_score(self, item: VideoItem) -> float:
        """20 % weight — how fresh the sound is."""
        days = item.sound_duration_days
        if days == 0:
            return 50.0
        if days <= 7:
            return 100.0
        if days <= 30:
            return 70.0
        if days <= 90:
            return 30.0
        return 10.0

    def _engagement_diversity_score(self, item: VideoItem) -> float:
        """20 % weight — Shannon entropy across likes, comments, shares, saves."""
        counts = np.array(
            [
                float(item.like_count),
                float(item.comment_count),
                float(item.share_count),
                float(item.save_count),
            ],
            dtype=np.float64,
        )

        total = counts.sum()
        if total == 0.0:
            return 0.0

        probs = counts / total
        # Compute entropy; suppress log(0) warnings by masking zeros
        nonzero = probs[probs > 0.0]
        entropy = float(-np.sum(nonzero * np.log(nonzero)))

        max_entropy = log(4)  # log(number of channels)
        if max_entropy == 0.0:
            return 0.0

        return min(entropy / max_entropy, 1.0) * 100.0
