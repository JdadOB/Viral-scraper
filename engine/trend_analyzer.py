from collections import defaultdict

from core.data_models import VideoItem


class TrendAnalyzer:
    """Extracts trend signals from a collection of VideoItems."""

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def extract_trending_hashtags(
        self, items: list[VideoItem], top_n: int = 20
    ) -> list[dict]:
        """
        Return the *top_n* hashtags sorted by usage count descending.

        Each entry: {"hashtag": str, "count": int,
                      "avg_virality": float, "platforms": list[str]}
        """
        if not items:
            return []

        tag_counts: dict[str, int] = defaultdict(int)
        tag_virality: dict[str, list[float]] = defaultdict(list)
        tag_platforms: dict[str, set[str]] = defaultdict(set)

        for item in items:
            for tag in item.hashtags:
                normalised = tag.lstrip("#").lower()
                tag_counts[normalised] += 1
                tag_virality[normalised].append(item.virality_score)
                tag_platforms[normalised].add(item.platform.value)

        results = [
            {
                "hashtag": tag,
                "count": tag_counts[tag],
                "avg_virality": round(
                    sum(tag_virality[tag]) / len(tag_virality[tag]), 4
                ),
                "platforms": sorted(tag_platforms[tag]),
            }
            for tag in tag_counts
        ]

        results.sort(key=lambda x: x["count"], reverse=True)
        return results[:top_n]

    def get_sound_trends(self, items: list[VideoItem]) -> list[dict]:
        """
        Return sounds that appear in more than one video, sorted by count desc.

        Each entry: {"sound_name": str, "count": int, "avg_virality": float}
        """
        if not items:
            return []

        sound_counts: dict[str, int] = defaultdict(int)
        sound_virality: dict[str, list[float]] = defaultdict(list)

        for item in items:
            name = item.sound_name.strip()
            if not name:
                continue
            sound_counts[name] += 1
            sound_virality[name].append(item.virality_score)

        results = [
            {
                "sound_name": sound,
                "count": sound_counts[sound],
                "avg_virality": round(
                    sum(sound_virality[sound]) / len(sound_virality[sound]), 4
                ),
            }
            for sound in sound_counts
            if sound_counts[sound] > 1
        ]

        results.sort(key=lambda x: x["count"], reverse=True)
        return results

    def platform_breakdown(self, items: list[VideoItem]) -> dict:
        """
        Return per-platform aggregate stats.

        Shape: {"tiktok": {"count": int, "avg_virality": float, "avg_views": float},
                "instagram": {...}}
        """
        platform_data: dict[str, dict[str, list]] = {}

        for item in items:
            key = item.platform.value
            if key not in platform_data:
                platform_data[key] = {"virality": [], "views": []}
            platform_data[key]["virality"].append(item.virality_score)
            platform_data[key]["views"].append(float(item.view_count))

        result: dict = {}
        for platform, data in platform_data.items():
            count = len(data["virality"])
            result[platform] = {
                "count": count,
                "avg_virality": round(sum(data["virality"]) / count, 4),
                "avg_views": round(sum(data["views"]) / count, 4),
            }

        return result

    def top_authors(
        self, items: list[VideoItem], top_n: int = 10
    ) -> list[dict]:
        """
        Return the *top_n* authors sorted by video count descending.

        Each entry: {"author": str, "platform": str,
                      "video_count": int, "avg_virality": float}

        When the same author name appears on multiple platforms, each
        (author, platform) combination is treated as a distinct entry.
        """
        if not items:
            return []

        # Key = (author, platform)
        author_counts: dict[tuple[str, str], int] = defaultdict(int)
        author_virality: dict[tuple[str, str], list[float]] = defaultdict(list)

        for item in items:
            key = (item.author, item.platform.value)
            author_counts[key] += 1
            author_virality[key].append(item.virality_score)

        results = [
            {
                "author": author,
                "platform": platform,
                "video_count": author_counts[(author, platform)],
                "avg_virality": round(
                    sum(author_virality[(author, platform)])
                    / author_counts[(author, platform)],
                    4,
                ),
            }
            for author, platform in author_counts
        ]

        results.sort(key=lambda x: x["video_count"], reverse=True)
        return results[:top_n]

    def virality_histogram(
        self, items: list[VideoItem], bins: int = 10
    ) -> dict:
        """
        Return histogram data for virality_score distribution.

        Shape: {"bins": list[float], "counts": list[int]}
        *bins* is the list of left-edge bin boundaries (length == bins+1).
        *counts* is the number of items that fall in each bin (length == bins).
        """
        if not items:
            return {"bins": [], "counts": []}

        scores = [item.virality_score for item in items]
        min_score = 0.0
        max_score = 100.0
        bin_width = (max_score - min_score) / bins

        bin_edges = [round(min_score + i * bin_width, 6) for i in range(bins + 1)]
        counts = [0] * bins

        for score in scores:
            if score >= max_score:
                # Place the maximum value in the last bin
                counts[-1] += 1
                continue
            idx = int((score - min_score) / bin_width)
            idx = min(max(idx, 0), bins - 1)
            counts[idx] += 1

        return {"bins": bin_edges, "counts": counts}
