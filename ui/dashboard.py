"""
ui/dashboard.py — Dashboard rendering functions for Viral Scraper.
"""
from __future__ import annotations

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

from core.data_models import VideoItem, Platform
from engine.trend_analyzer import TrendAnalyzer
from ui.components import metric_card, render_cards_grid, trend_pill, empty_state


# ---------------------------------------------------------------------------
# Colour palette constants
# ---------------------------------------------------------------------------
_BG_DARK = "#1A1A2E"
_BG_CARD = "#16213E"
_LAVENDER = "#B57EDC"
_LAVENDER_LIGHT = "#D4A8F0"
_RED_ACCENT = "#E94560"
_TIKTOK_CYAN = "#69C9D0"
_INSTAGRAM_PINK = "#E1306C"
_TEXT_PRIMARY = "#E0E0E0"
_TEXT_SECONDARY = "#A0A0B0"


def _plotly_layout_defaults() -> dict:
    """Return a dict of common plotly layout overrides for the dark theme."""
    return dict(
        paper_bgcolor=_BG_DARK,
        plot_bgcolor=_BG_CARD,
        font=dict(family="Inter, system-ui, sans-serif", color=_TEXT_PRIMARY, size=12),
        margin=dict(l=40, r=20, t=40, b=40),
        legend=dict(
            bgcolor="rgba(22,33,62,0.8)",
            bordercolor="rgba(181,126,220,0.25)",
            borderwidth=1,
            font=dict(color=_TEXT_PRIMARY),
        ),
    )


def _fmt_number(n: int | float) -> str:
    n = int(n)
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


# ---------------------------------------------------------------------------
# render_summary_metrics
# ---------------------------------------------------------------------------

def render_summary_metrics(items: list[VideoItem]) -> None:
    """Render top-row summary metric cards: Total Videos, Avg Virality,
    Total Views, Top Platform."""
    if not items:
        return

    total_videos = len(items)
    avg_virality = sum(i.virality_score for i in items) / total_videos
    total_views = sum(i.view_count or i.play_count for i in items)

    # Determine top platform
    tiktok_count = sum(1 for i in items if i.platform == Platform.TIKTOK)
    instagram_count = total_videos - tiktok_count
    top_platform = "TikTok" if tiktok_count >= instagram_count else "Instagram"

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            metric_card(
                title="Total Videos",
                value=str(total_videos),
                icon="🎬",
            ),
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            metric_card(
                title="Avg Virality",
                value=f"{avg_virality:.1f}",
                icon="⚡",
            ),
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            metric_card(
                title="Total Views",
                value=_fmt_number(total_views),
                icon="👁",
            ),
            unsafe_allow_html=True,
        )

    with col4:
        icon = "🎵" if top_platform == "TikTok" else "📷"
        st.markdown(
            metric_card(
                title="Top Platform",
                value=top_platform,
                icon=icon,
            ),
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------------------------
# render_discovery_dashboard
# ---------------------------------------------------------------------------

def render_discovery_dashboard(
    items: list[VideoItem],
    richey_scores: dict,
    settings: dict,
) -> None:
    """Sort and filter items per settings, then render the video card grid."""
    if not items:
        empty_state("No content found. Try scraping a hashtag or keyword.")
        return

    # --- Apply virality floor -------------------------------------------
    min_virality = settings.get("min_virality", 0)
    filtered = [i for i in items if i.virality_score >= min_virality]

    # --- Apply richey filter --------------------------------------------
    if settings.get("richey_only", False):
        min_richey = settings.get("min_richey", 0.6)
        filtered = [i for i in filtered if richey_scores.get(i.id, 0.0) >= min_richey]

    # --- Sort -----------------------------------------------------------
    sort_by = settings.get("sort_by", "Virality Score")
    if sort_by == "Views":
        filtered.sort(key=lambda i: (i.view_count or i.play_count), reverse=True)
    elif sort_by == "Likes":
        filtered.sort(key=lambda i: i.like_count, reverse=True)
    elif sort_by == "Recent":
        filtered.sort(
            key=lambda i: (i.posted_at.timestamp() if i.posted_at else 0.0),
            reverse=True,
        )
    else:  # "Virality Score" (default)
        filtered.sort(key=lambda i: i.virality_score, reverse=True)

    # --- Apply max results cap ------------------------------------------
    max_results = settings.get("max_results", 50)
    filtered = filtered[:max_results]

    if not filtered:
        empty_state(
            f"No videos matched your filters "
            f"(virality ≥ {min_virality}, richey ≥ {settings.get('min_richey', 0.6):.2f})."
        )
        return

    # --- Summary bar ---------------------------------------------------
    st.markdown(
        f'<div style="color:{_TEXT_SECONDARY};font-size:0.82rem;margin-bottom:1rem;">'
        f'Showing <b style="color:{_LAVENDER};">{len(filtered)}</b> of '
        f'<b style="color:{_LAVENDER};">{len(items)}</b> videos</div>',
        unsafe_allow_html=True,
    )

    # --- Render grid ---------------------------------------------------
    card_cols = settings.get("card_cols", 3)
    render_cards_grid(filtered, richey_scores, cols=card_cols)


# ---------------------------------------------------------------------------
# render_trends_map
# ---------------------------------------------------------------------------

def render_trends_map(items: list[VideoItem], analyzer: TrendAnalyzer) -> None:
    """Render the Trends tab: hashtag pills, bar chart, sound trends,
    and platform breakdown donut chart."""
    if not items:
        empty_state("Scrape some content first to see trend data.")
        return

    # ------------------------------------------------------------------ #
    # Top hashtag pills (flowing layout)
    # ------------------------------------------------------------------ #
    st.markdown(
        '<div style="font-size:1rem;font-weight:700;color:#E0E0E0;'
        'margin-bottom:0.75rem;">🏷️ Trending Hashtags</div>',
        unsafe_allow_html=True,
    )

    top_tags = analyzer.extract_trending_hashtags(items, top_n=30)

    if top_tags:
        # Determine "hot" threshold = top quartile by count
        counts = [t["count"] for t in top_tags]
        hot_threshold = counts[len(counts) // 4] if len(counts) >= 4 else counts[0]

        pills_html = '<div style="line-height:2.2;">'
        for tag_data in top_tags:
            is_hot = tag_data["count"] >= hot_threshold
            pills_html += trend_pill(tag_data["hashtag"], tag_data["count"], is_hot=is_hot)
        pills_html += "</div>"

        st.markdown(pills_html, unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div style="color:{_TEXT_SECONDARY};">No hashtags found in results.</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------------------------------------------------------ #
    # Plotly bar chart: top 15 hashtags
    # ------------------------------------------------------------------ #
    if top_tags:
        top15 = top_tags[:15]
        labels = [f"#{t['hashtag']}" for t in top15]
        bar_counts = [t["count"] for t in top15]
        avg_viralities = [t["avg_virality"] for t in top15]

        bar_colors = [
            _RED_ACCENT if c >= hot_threshold else _LAVENDER for c in bar_counts
        ]

        fig_bar = go.Figure(
            data=[
                go.Bar(
                    x=labels,
                    y=bar_counts,
                    marker_color=bar_colors,
                    marker_line_color="rgba(255,255,255,0.05)",
                    marker_line_width=1,
                    hovertemplate=(
                        "<b>%{x}</b><br>"
                        "Count: %{y}<br>"
                        "Avg Virality: %{customdata:.1f}<extra></extra>"
                    ),
                    customdata=avg_viralities,
                    text=bar_counts,
                    textposition="outside",
                    textfont=dict(color=_TEXT_SECONDARY, size=10),
                )
            ]
        )
        fig_bar.update_layout(
            title=dict(
                text="Top 15 Hashtags by Usage",
                font=dict(color=_TEXT_PRIMARY, size=14),
                x=0,
            ),
            xaxis=dict(
                tickangle=-35,
                tickfont=dict(color=_TEXT_SECONDARY, size=10),
                gridcolor="rgba(255,255,255,0.04)",
                showgrid=False,
            ),
            yaxis=dict(
                tickfont=dict(color=_TEXT_SECONDARY),
                gridcolor="rgba(181,126,220,0.08)",
                showgrid=True,
            ),
            hoverlabel=dict(
                bgcolor=_BG_CARD,
                bordercolor=_LAVENDER,
                font_color=_TEXT_PRIMARY,
            ),
            bargap=0.25,
            template="plotly_dark",
            **_plotly_layout_defaults(),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # ------------------------------------------------------------------ #
    # Sound trends (sparkline-style virality bars)
    # ------------------------------------------------------------------ #
    sound_trends = analyzer.get_sound_trends(items)

    st.markdown(
        '<div style="font-size:1rem;font-weight:700;color:#E0E0E0;'
        'margin:1.5rem 0 0.75rem;">🎵 Trending Sounds</div>',
        unsafe_allow_html=True,
    )

    if sound_trends:
        max_virality = max((s["avg_virality"] for s in sound_trends), default=100.0)
        max_virality = max(max_virality, 1.0)

        rows_html = '<div class="glass-card" style="padding:1rem;">'
        for sound in sound_trends[:15]:
            bar_pct = int((sound["avg_virality"] / max_virality) * 100)
            name_safe = sound["sound_name"].replace("<", "&lt;").replace(">", "&gt;")
            rows_html += (
                f'<div class="sound-row">'
                f'  <div class="sound-name" title="{name_safe}">{name_safe}</div>'
                f'  <div class="sound-count">×{sound["count"]}</div>'
                f'  <div class="sound-virality-bar">'
                f'    <div class="sound-virality-fill" style="width:{bar_pct}%;"></div>'
                f'  </div>'
                f'  <div style="font-size:0.72rem;color:{_LAVENDER};min-width:3rem;text-align:right;">'
                f'    {sound["avg_virality"]:.0f}⚡'
                f'  </div>'
                f'</div>'
            )
        rows_html += "</div>"
        st.markdown(rows_html, unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div style="color:{_TEXT_SECONDARY};">Not enough repeated sounds to surface trends.</div>',
            unsafe_allow_html=True,
        )

    # ------------------------------------------------------------------ #
    # Platform breakdown donut chart
    # ------------------------------------------------------------------ #
    st.markdown(
        '<div style="font-size:1rem;font-weight:700;color:#E0E0E0;'
        'margin:1.5rem 0 0.75rem;">📊 Platform Breakdown</div>',
        unsafe_allow_html=True,
    )

    breakdown = analyzer.platform_breakdown(items)

    if breakdown:
        plat_labels = [k.capitalize() for k in breakdown.keys()]
        plat_values = [v["count"] for v in breakdown.values()]
        plat_colors = [
            _TIKTOK_CYAN if k == "tiktok" else _INSTAGRAM_PINK
            for k in breakdown.keys()
        ]

        fig_donut = go.Figure(
            data=[
                go.Pie(
                    labels=plat_labels,
                    values=plat_values,
                    hole=0.55,
                    marker=dict(
                        colors=plat_colors,
                        line=dict(color=_BG_DARK, width=3),
                    ),
                    textfont=dict(color=_TEXT_PRIMARY, size=12),
                    hovertemplate=(
                        "<b>%{label}</b><br>"
                        "Videos: %{value}<br>"
                        "%{percent}<extra></extra>"
                    ),
                )
            ]
        )
        fig_donut.update_layout(
            title=dict(
                text="Videos per Platform",
                font=dict(color=_TEXT_PRIMARY, size=14),
                x=0,
            ),
            annotations=[
                dict(
                    text=f"<b>{sum(plat_values)}</b><br>Total",
                    x=0.5,
                    y=0.5,
                    font=dict(size=14, color=_TEXT_PRIMARY),
                    showarrow=False,
                )
            ],
            showlegend=True,
            template="plotly_dark",
            **_plotly_layout_defaults(),
        )
        st.plotly_chart(fig_donut, use_container_width=True)


# ---------------------------------------------------------------------------
# render_virality_chart
# ---------------------------------------------------------------------------

def render_virality_chart(items: list[VideoItem]) -> None:
    """Render a Plotly scatter plot: x=views, y=likes, size=virality_score,
    color=platform, matching the dark app theme."""
    if not items:
        empty_state("Scrape some content first to see analytics.")
        return

    views = [i.view_count or i.play_count for i in items]
    likes = [i.like_count for i in items]
    virality = [max(i.virality_score, 1.0) for i in items]
    platforms = [i.platform.value.capitalize() for i in items]
    authors = [f"@{i.author}" if i.author else "Unknown" for i in items]
    descriptions = [
        (i.description[:60] + "…") if len(i.description) > 60 else i.description
        for i in items
    ]

    color_map = {
        "Tiktok": _TIKTOK_CYAN,
        "Instagram": _INSTAGRAM_PINK,
    }

    # Build traces per platform for clean legend
    fig = go.Figure()

    for plat, color in color_map.items():
        mask = [p == plat for p in platforms]
        if not any(mask):
            continue

        p_views = [v for v, m in zip(views, mask) if m]
        p_likes = [l for l, m in zip(likes, mask) if m]
        p_virality = [v for v, m in zip(virality, mask) if m]
        p_authors = [a for a, m in zip(authors, mask) if m]
        p_descs = [d for d, m in zip(descriptions, mask) if m]
        p_scores = [i.virality_score for i, m in zip(items, mask) if m]

        fig.add_trace(
            go.Scatter(
                x=p_views,
                y=p_likes,
                mode="markers",
                name=plat,
                marker=dict(
                    size=[max(8, min(s / 3, 40)) for s in p_virality],
                    color=color,
                    opacity=0.75,
                    line=dict(color="rgba(255,255,255,0.2)", width=1),
                    sizemode="area",
                ),
                customdata=list(zip(p_authors, p_scores, p_descs)),
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    "Views: %{x:,}<br>"
                    "Likes: %{y:,}<br>"
                    "Virality: %{customdata[1]:.1f}<br>"
                    "<i>%{customdata[2]}</i><extra></extra>"
                ),
            )
        )

    fig.update_layout(
        title=dict(
            text="Virality Scatter — Views vs Likes (bubble size = virality score)",
            font=dict(color=_TEXT_PRIMARY, size=14),
            x=0,
        ),
        xaxis=dict(
            title=dict(text="Views", font=dict(color=_TEXT_SECONDARY)),
            tickfont=dict(color=_TEXT_SECONDARY),
            gridcolor="rgba(181,126,220,0.08)",
            showgrid=True,
            zeroline=False,
        ),
        yaxis=dict(
            title=dict(text="Likes", font=dict(color=_TEXT_SECONDARY)),
            tickfont=dict(color=_TEXT_SECONDARY),
            gridcolor="rgba(181,126,220,0.08)",
            showgrid=True,
            zeroline=False,
        ),
        hoverlabel=dict(
            bgcolor=_BG_CARD,
            bordercolor=_LAVENDER,
            font_color=_TEXT_PRIMARY,
        ),
        template="plotly_dark",
        height=520,
        **_plotly_layout_defaults(),
    )

    st.plotly_chart(fig, use_container_width=True)

    # ------------------------------------------------------------------ #
    # Virality histogram
    # ------------------------------------------------------------------ #
    st.markdown(
        '<div style="font-size:1rem;font-weight:700;color:#E0E0E0;'
        'margin:1.5rem 0 0.75rem;">⚡ Virality Score Distribution</div>',
        unsafe_allow_html=True,
    )

    scores = [i.virality_score for i in items]

    fig_hist = go.Figure(
        data=[
            go.Histogram(
                x=scores,
                nbinsx=20,
                marker_color=_LAVENDER,
                marker_line_color="rgba(255,255,255,0.08)",
                marker_line_width=1,
                opacity=0.85,
                hovertemplate="Range: %{x}<br>Count: %{y}<extra></extra>",
            )
        ]
    )
    fig_hist.update_layout(
        title=dict(
            text="Distribution of Virality Scores",
            font=dict(color=_TEXT_PRIMARY, size=14),
            x=0,
        ),
        xaxis=dict(
            title=dict(text="Virality Score (0–100)", font=dict(color=_TEXT_SECONDARY)),
            tickfont=dict(color=_TEXT_SECONDARY),
            gridcolor="rgba(181,126,220,0.08)",
        ),
        yaxis=dict(
            title=dict(text="Number of Videos", font=dict(color=_TEXT_SECONDARY)),
            tickfont=dict(color=_TEXT_SECONDARY),
            gridcolor="rgba(181,126,220,0.08)",
        ),
        bargap=0.05,
        template="plotly_dark",
        height=360,
        **_plotly_layout_defaults(),
    )
    st.plotly_chart(fig_hist, use_container_width=True)
