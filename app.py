"""
Viral Content Scraper — Streamlit App
Run: streamlit run app.py
"""
from __future__ import annotations

import asyncio
import logging
import os

import streamlit as st
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Page config — must be the very first Streamlit call
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="🔮 Viral Scraper",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load .env for local development; Streamlit Cloud uses st.secrets instead
load_dotenv()

# ---------------------------------------------------------------------------
# Internal imports (after dotenv so env vars are present)
# ---------------------------------------------------------------------------
from config.settings import AppSettings
from core.apify_client import ApifyClientWrapper
from core.tiktok_scraper import TikTokScraper
from core.instagram_scraper import InstagramScraper
from core.data_models import VideoItem
from engine.virality_scorer import ViralityScorer
from engine.trend_analyzer import TrendAnalyzer
from ui.styles import inject_css
from ui.sidebar import render_sidebar
from ui.dashboard import (
    render_summary_metrics,
    render_discovery_dashboard,
    render_trends_map,
    render_virality_chart,
)
from ui.components import empty_state
from utils.async_helpers import run_async

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Secrets resolution — st.secrets (Streamlit Cloud) > env vars > error
# ---------------------------------------------------------------------------

def _resolve_secret(key: str, default: str | None = None) -> str | None:
    """Read a secret from st.secrets first, then fall back to env vars."""
    try:
        return str(st.secrets[key])
    except (KeyError, AttributeError):
        pass
    return os.getenv(key, default)


def _build_app_settings() -> AppSettings:
    """Build AppSettings from st.secrets / env vars. Raises on missing token."""
    token = _resolve_secret("APIFY_API_TOKEN", "")
    if not token:
        raise EnvironmentError(
            "APIFY_API_TOKEN is not set. "
            "Add it to .streamlit/secrets.toml (local) or the Streamlit Cloud "
            "Secrets panel, or set it as an environment variable."
        )
    return AppSettings(
        apify_api_token=token,
        tiktok_actor_id=_resolve_secret("TIKTOK_ACTOR_ID", "clockworks/tiktok-scraper"),
        instagram_actor_id=_resolve_secret("INSTAGRAM_ACTOR_ID", "apify/instagram-scraper"),
        max_results_per_query=int(_resolve_secret("MAX_RESULTS_PER_QUERY", "50")),
        proxy_rotation_enabled=_resolve_secret("PROXY_ROTATION_ENABLED", "true").lower() == "true",
        cache_ttl_seconds=int(_resolve_secret("CACHE_TTL_SECONDS", "300")),
    )


# ---------------------------------------------------------------------------
# Cached resource — one Apify client per Streamlit session lifetime
# ---------------------------------------------------------------------------

@st.cache_resource(show_spinner=False)
def _get_apify_client(token: str, proxy_rotation_enabled: bool = True) -> ApifyClientWrapper:
    return ApifyClientWrapper(api_token=token, proxy_rotation_enabled=proxy_rotation_enabled)


# ---------------------------------------------------------------------------
# Scraping (sync wrapper around the async pipeline)
# ---------------------------------------------------------------------------

async def _scrape_async(
    settings_obj: AppSettings,
    query: str,
    platforms: list[str],
    max_results: int,
) -> list[VideoItem]:
    client = _get_apify_client(settings_obj.apify_api_token, settings_obj.proxy_rotation_enabled)
    tasks = []

    is_hashtag = query.startswith("#")
    clean_query = query.lstrip("#").strip()

    if "tiktok" in platforms:
        scraper = TikTokScraper(client=client, settings=settings_obj)
        tasks.append(
            scraper.scrape_hashtag(clean_query, max_results=max_results)
            if is_hashtag
            else scraper.scrape_keyword(clean_query, max_results=max_results)
        )

    if "instagram" in platforms:
        scraper = InstagramScraper(client=client, settings=settings_obj)
        tasks.append(
            scraper.scrape_hashtag(clean_query, max_results=max_results)
            if is_hashtag
            else scraper.scrape_keyword(clean_query, max_results=max_results)
        )

    if not tasks:
        return []

    results = await asyncio.gather(*tasks, return_exceptions=True)
    items: list[VideoItem] = []
    for result in results:
        if isinstance(result, Exception):
            logger.warning("Scraper task failed: %s", result)
            continue
        if result.success:
            items.extend(result.items)
        else:
            logger.warning("Scraper failure [%s]: %s", result.platform, result.error_message)
    return items


def _run_scrape(
    settings_obj: AppSettings,
    query: str,
    platforms: list[str],
    max_results: int,
) -> list[VideoItem]:
    # run_async handles Streamlit's running event loop safely
    return run_async(_scrape_async(settings_obj, query, platforms, max_results))


# ---------------------------------------------------------------------------
# Hero welcome section
# ---------------------------------------------------------------------------

def _render_hero() -> None:
    st.markdown(
        """
        <div style="text-align:center;padding:3rem 1rem 2rem;">
          <div class="hero-title">Discover What's Going Viral</div>
          <div class="hero-subtitle">
            Powered by real-time Apify scraping + AI virality analysis
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            """
            <div class="glass-card" style="text-align:center;padding:2rem 1.5rem;">
              <span class="hero-feature-icon">🎬</span>
              <div class="hero-feature-title">Multi-Platform</div>
              <div class="hero-feature-desc">
                Scrape TikTok and Instagram simultaneously.
                Enter any hashtag or keyword and get results
                from both platforms in a single click.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """
            <div class="glass-card" style="text-align:center;padding:2rem 1.5rem;">
              <span class="hero-feature-icon">🧬</span>
              <div class="hero-feature-title">Virality Engine</div>
              <div class="hero-feature-desc">
                Four-dimensional virality scoring based on
                engagement velocity, save-to-view ratio,
                sound freshness, and engagement diversity.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            """
            <div class="glass-card" style="text-align:center;padding:2rem 1.5rem;">
              <span class="hero-feature-icon">💎</span>
              <div class="hero-feature-title">Richey Filter</div>
              <div class="hero-feature-desc">
                Premium brand-quality filter that scores
                production value, engagement quality, optimal
                content length, and curated hashtag usage.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="glass-card" style="max-width:640px;margin:0 auto;text-align:center;padding:1.5rem 2rem;">
          <div style="font-family:'Courier New',monospace;font-size:0.78rem;
                      color:#B57EDC;line-height:1.8;letter-spacing:0.04em;">
            ╔══════════════════════════════════╗<br>
            ║  &nbsp;1. Enter a hashtag or keyword&nbsp;&nbsp; ║<br>
            ║  &nbsp;2. Select your platforms&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ║<br>
            ║  &nbsp;3. Click 🚀 Scrape Now&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ║<br>
            ║  &nbsp;4. Explore viral content&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ║<br>
            ╚══════════════════════════════════╝
          </div>
          <div style="margin-top:1rem;font-size:0.82rem;color:#A0A0B0;">
            Use the sidebar on the left to configure scraping options.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Tab renderer
# ---------------------------------------------------------------------------

def _render_tabs(tab_discovery, tab_trends, tab_analytics, settings: dict) -> None:
    items: list[VideoItem] = st.session_state.get("items", [])
    analyzer = TrendAnalyzer()

    if items:
        # Pre-filter so summary metrics match what the grid shows
        min_virality = settings.get("min_virality", 0)
        visible = [i for i in items if i.virality_score >= min_virality]

        with tab_discovery:
            render_summary_metrics(visible)
            st.markdown("<br>", unsafe_allow_html=True)
            render_discovery_dashboard(items, settings)
        with tab_trends:
            render_trends_map(items, analyzer)
        with tab_analytics:
            render_virality_chart(items)
    else:
        with tab_discovery:
            _render_hero()
        with tab_trends:
            empty_state("Scrape some content first to explore trends.")
        with tab_analytics:
            empty_state("Scrape some content first to see analytics charts.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    inject_css()
    settings = render_sidebar()

    st.markdown(
        '<h1 class="gradient-title">🔮 Viral Scraper</h1>',
        unsafe_allow_html=True,
    )

    tab_discovery, tab_trends, tab_analytics = st.tabs(
        ["🎯 Discovery", "📈 Trends", "⚡ Analytics"]
    )

    if settings["scrape_clicked"]:
        query = settings["query"]
        platforms = settings["platforms"]

        if not query:
            st.warning("Please enter a hashtag or keyword before scraping.")
        elif not platforms:
            st.warning("Please select at least one platform.")
        else:
            try:
                app_settings = _build_app_settings()
            except EnvironmentError as exc:
                st.error(f"⚠️ Configuration error: {exc}")
                _render_tabs(tab_discovery, tab_trends, tab_analytics, settings)
                return

            with st.spinner(f'Scraping viral content for "{query}"…'):
                try:
                    # Fetch 5× the target so filters have candidates to replace
                    # removed videos; cap at 200 to avoid excessive API usage
                    target = settings["max_results"]
                    fetch_count = min(target * 5, 200)
                    raw_items = _run_scrape(
                        settings_obj=app_settings,
                        query=query,
                        platforms=platforms,
                        max_results=fetch_count,
                    )
                except Exception as exc:
                    st.error(
                        f"Scraping failed: {exc}. "
                        "Check your APIFY_API_TOKEN and network connection."
                    )
                    logger.exception("Scraping error")
                    _render_tabs(tab_discovery, tab_trends, tab_analytics, settings)
                    return

            if not raw_items:
                st.warning(
                    "No results returned. The query may have no content or "
                    "the Apify actors may need more time. Try again."
                )
                _render_tabs(tab_discovery, tab_trends, tab_analytics, settings)
                return

            scorer = ViralityScorer()
            scored_items = scorer.score_batch(raw_items)

            from datetime import datetime, timedelta
            cutoff = datetime.utcnow() - timedelta(days=30)

            # Apply all hard filters — no missing data allowed
            filtered_items: list[VideoItem] = []
            recent, low_views, small_account, no_data = [], [], [], []
            for item in scored_items:
                views = item.view_count or item.play_count
                followers = item.follower_count

                # Drop if date unknown or too old
                if item.posted_at is None:
                    no_data.append(item)
                    continue
                if item.posted_at.replace(tzinfo=None) < cutoff:
                    recent.append(item)
                    continue
                # Drop if view count unknown or under 40k
                if views < 40_000:
                    low_views.append(item)
                    continue
                # Drop if follower count unknown or under 10k
                if followers < 10_000:
                    small_account.append(item)
                    continue

                filtered_items.append(item)

            # Trim to the user's requested target (already sorted by virality)
            shown = filtered_items[:target]
            st.session_state["items"] = shown

            msg = f"✅ Showing {len(shown)} of {target} requested"
            if len(shown) < target:
                msg += f" — only {len(shown)} passed all filters"
            msg += f" (fetched {len(raw_items)} candidates)."
            notes = []
            if recent:
                notes.append(f"{len(recent)} too old")
            if low_views:
                notes.append(f"{len(low_views)} under 40k views")
            if small_account:
                notes.append(f"{len(small_account)} under 10k followers")
            if no_data:
                notes.append(f"{len(no_data)} missing data")
            if notes:
                msg += f" Filtered out: {', '.join(notes)}."
            st.success(msg)

    _render_tabs(tab_discovery, tab_trends, tab_analytics, settings)


if __name__ == "__main__":
    main()
