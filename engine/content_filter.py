from core.data_models import VideoItem


class ContentFilter:
    """Filters VideoItem lists for 'richey' premium brand content."""

    # Production quality signals
    QUALITY_KEYWORDS: list[str] = [
        "cinematic",
        "aesthetic",
        "editorial",
        "luxury",
        "premium",
        "curated",
        "artisan",
        "handcrafted",
        "minimal",
        "clean",
    ]

    SPAM_INDICATORS: list[str] = [
        "follow for follow",
        "f4f",
        "like4like",
        "giveaway spam",
    ]

    # Sub-score weights (must sum to 1.0)
    W_PRODUCTION = 0.30
    W_ENGAGEMENT = 0.25
    W_LENGTH = 0.25
    W_HASHTAG = 0.20

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def filter(
        self, items: list[VideoItem], min_richey_score: float = 0.6
    ) -> list[VideoItem]:
        """Return only items whose Richey score is >= *min_richey_score*."""
        return [item for item in items if self.richey_score(item) >= min_richey_score]

    def richey_score(self, item: VideoItem) -> float:
        """Return a Richey premium brand score in [0, 1]."""
        production = self._production_quality_score(item)
        engagement = self._engagement_quality_score(item)
        length = self._content_length_score(item)
        hashtag = self._hashtag_quality_score(item)

        raw = (
            production * self.W_PRODUCTION
            + engagement * self.W_ENGAGEMENT
            + length * self.W_LENGTH
            + hashtag * self.W_HASHTAG
        )
        return round(min(max(raw, 0.0), 1.0), 6)

    def annotate(self, items: list[VideoItem]) -> list[dict]:
        """Return each item as a dict with an extra 'richey_score' key."""
        results: list[dict] = []
        for item in items:
            data = item.model_dump()
            data["richey_score"] = self.richey_score(item)
            results.append(data)
        return results

    # ------------------------------------------------------------------ #
    # Sub-scores                                                           #
    # ------------------------------------------------------------------ #

    def _production_quality_score(self, item: VideoItem) -> float:
        """
        Keyword-based production quality.

        Each quality keyword present in the lowercased description adds +0.1
        (capped at +0.4). Each spam indicator subtracts 0.2. Final value is
        clamped to [0, 1].
        """
        text = item.description.lower()

        keyword_hits = sum(1 for kw in self.QUALITY_KEYWORDS if kw in text)
        keyword_score = min(keyword_hits * 0.1, 0.4)

        spam_penalty = sum(0.2 for sp in self.SPAM_INDICATORS if sp in text)

        # Start from a baseline of 0.5 so neutral content is in the middle
        # The spec states +0.1 per keyword (max 0.4) and -0.2 per spam hit.
        # We interpret the combined result as a direct score component.
        raw = keyword_score - spam_penalty
        return min(max(raw + 0.6, 0.0), 1.0)  # shift: neutral description → 0.6

    def _engagement_quality_score(self, item: VideoItem) -> float:
        """
        Comment-to-like ratio quality.

        Ideal range 0.02–0.08 → score 1.0; outside that range scales linearly
        toward 0 at the edges (0 → 0 and 0.5+ → 0 beyond ideal).
        """
        ratio = item.comment_count / max(item.like_count, 1)

        if 0.02 <= ratio <= 0.08:
            return 1.0

        if ratio < 0.02:
            # Linear 0 at ratio=0 to 1 at ratio=0.02
            return ratio / 0.02

        # ratio > 0.08: linear 1 at 0.08, reaching 0 at ratio=0.50
        return max(1.0 - (ratio - 0.08) / (0.50 - 0.08), 0.0)

    def _content_length_score(self, item: VideoItem) -> float:
        """Duration-based content quality."""
        seconds = item.duration_seconds

        if 15.0 <= seconds <= 60.0:
            return 1.0
        if seconds <= 120.0:
            return 0.7
        return 0.4

    def _hashtag_quality_score(self, item: VideoItem) -> float:
        """Hashtag count quality (fewer = more curated)."""
        count = len(item.hashtags)

        if count < 5:
            return 1.0
        if count <= 15:
            return 0.7
        return 0.3
