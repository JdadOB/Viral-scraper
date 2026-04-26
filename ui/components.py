"""
ui/components.py — Reusable glassmorphic HTML components for Viral Scraper.
"""
from __future__ import annotations

import streamlit as st

from core.data_models import VideoItem, Platform


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fmt_number(n: int | float) -> str:
    """Format large numbers as 1.2K / 3.4M etc."""
    n = int(n)
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def _platform_badge(platform: Platform) -> str:
    if platform == Platform.TIKTOK:
        return '<span class="platform-badge-tiktok">TikTok</span>'
    return '<span class="platform-badge-instagram">Instagram</span>'


def _truncate(text: str, max_len: int = 100) -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len].rstrip() + "…"


# ---------------------------------------------------------------------------
# video_card
# ---------------------------------------------------------------------------

def video_card(item: VideoItem) -> str:
    """Return an HTML string for a glassmorphic video card."""
    # --- Thumbnail -------------------------------------------------------
    if item.thumbnail_url:
        thumb_html = (
            f'<img src="{item.thumbnail_url}" '
            f'class="video-card-thumb" alt="thumbnail" loading="lazy" />'
        )
    else:
        thumb_html = (
            '<div class="video-card-thumb-placeholder">🎬</div>'
        )

    # --- Virality score badge --------------------------------------------
    score_int = int(round(item.virality_score))
    score_badge = f'<span class="score-badge">⚡ {score_int}</span>'

    # --- Platform badge --------------------------------------------------
    plat_badge = _platform_badge(item.platform)

    # --- Author + description -------------------------------------------
    author_html = (
        f'<div class="video-card-author">@{item.author}</div>'
        if item.author
        else '<div class="video-card-author">&nbsp;</div>'
    )
    desc_safe = _truncate(item.description, 100).replace("<", "&lt;").replace(">", "&gt;")
    desc_html = f'<div class="video-card-desc">{desc_safe}</div>'

    # --- Metrics row -----------------------------------------------------
    views = _fmt_number(item.view_count or item.play_count)
    likes = _fmt_number(item.like_count)
    comments = _fmt_number(item.comment_count)
    saves = _fmt_number(item.save_count)

    metrics_html = (
        '<div class="video-card-metrics">'
        f'<span class="video-card-metric">👁 <span class="metric-num">{views}</span></span>'
        f'<span class="video-card-metric">❤️ <span class="metric-num">{likes}</span></span>'
        f'<span class="video-card-metric">💬 <span class="metric-num">{comments}</span></span>'
        f'<span class="video-card-metric">🔖 <span class="metric-num">{saves}</span></span>'
        '</div>'
    )

    # --- Posted date -----------------------------------------------------
    if item.posted_at:
        from datetime import datetime
        delta = datetime.utcnow() - item.posted_at.replace(tzinfo=None)
        days = delta.days
        if days == 0:
            age_str = "Today"
        elif days == 1:
            age_str = "Yesterday"
        elif days < 7:
            age_str = f"{days}d ago"
        elif days < 30:
            age_str = f"{days // 7}w ago"
        else:
            age_str = f"{days}d ago"
        date_html = f'<div class="video-card-date">🕐 {age_str}</div>'
    else:
        date_html = ""

    # --- View/follower ratio badge (viral signal) -------------------------
    views = item.view_count or item.play_count
    if item.follower_count > 0 and views > 0:
        ratio = views / item.follower_count
        ratio_html = (
            f'<div class="viral-ratio">📡 {ratio:.0f}× reach</div>'
        )
    else:
        ratio_html = ""

    # --- Hashtag pills (first 5) -----------------------------------------
    tags = item.hashtags[:5]
    pills = "".join(
        f'<span class="trend-pill">#{tag}</span>' for tag in tags
    )
    tags_html = f'<div class="video-card-tags">{pills}</div>' if pills else ""

    # --- Open button -----------------------------------------------------
    url = item.url or "#"
    open_btn = (
        f'<a href="{url}" target="_blank" rel="noopener noreferrer" '
        f'class="video-card-open-btn">Open ↗</a>'
    )

    # --- Assemble --------------------------------------------------------
    return f"""
<div class="glass-card" style="padding:1rem;">
  {thumb_html}
  <div class="video-card-header">
    <div style="display:flex;gap:0.4rem;align-items:center;flex-wrap:wrap;">
      {plat_badge}
      {author_html}
    </div>
    {score_badge}
  </div>
  {date_html}
  {desc_html}
  {metrics_html}
  {ratio_html}
  {tags_html}
  {open_btn}
</div>
"""


# ---------------------------------------------------------------------------
# metric_card
# ---------------------------------------------------------------------------

def metric_card(title: str, value: str, delta: str = "", icon: str = "") -> str:
    """Return HTML for a summary metric glass card."""
    icon_html = f'<span style="font-size:1.4rem;margin-bottom:0.4rem;display:block;">{icon}</span>' if icon else ""

    if delta:
        # Determine colour by leading sign
        delta_class = "metric-delta-down" if delta.startswith("-") else "metric-delta-up"
        delta_html = f'<div class="{delta_class}">{delta}</div>'
    else:
        delta_html = ""

    return f"""
<div class="glass-card" style="text-align:center;padding:1.25rem 1rem;">
  {icon_html}
  <div class="metric-value">{value}</div>
  <div class="metric-label">{title}</div>
  {delta_html}
</div>
"""


# ---------------------------------------------------------------------------
# trend_pill
# ---------------------------------------------------------------------------

def trend_pill(tag: str, count: int, is_hot: bool = False) -> str:
    """Return HTML for a hashtag trend pill."""
    css_class = "hot-badge" if is_hot else "trend-pill"
    label = tag if tag.startswith("#") else f"#{tag}"
    return f'<span class="{css_class}">{label} <b>{count}</b></span>'


# ---------------------------------------------------------------------------
# render_cards_grid
# ---------------------------------------------------------------------------

def render_cards_grid(items: list[VideoItem], cols: int = 3) -> None:
    """Render a CSS grid of video cards using st.columns."""
    if not items:
        empty_state()
        return

    columns = st.columns(cols)
    for idx, item in enumerate(items):
        with columns[idx % cols]:
            st.markdown(video_card(item), unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# empty_state
# ---------------------------------------------------------------------------

def empty_state(message: str = "No content found. Try a different search.") -> None:
    """Render a centered empty state illustration."""
    html = f"""
<div class="empty-state">
  <div class="empty-state-icon">🔍</div>
  <div class="empty-state-title">{message}</div>
</div>
"""
    st.markdown(html, unsafe_allow_html=True)
