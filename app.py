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
        instagram_actor_id=_resolve_secret("INSTAGRAM_ACTOR_ID", "apify/instagram-hashtag-scraper"),
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
    runs_per_platform: int = 5,
) -> list[VideoItem]:
    """Run `runs_per_platform` parallel calls per platform, merge and deduplicate."""
    client = _get_apify_client(settings_obj.apify_api_token, settings_obj.proxy_rotation_enabled)

    is_hashtag = query.startswith("#")
    clean_query = query.lstrip("#").strip()

    tasks = []

    for _ in range(runs_per_platform):
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

    # Merge, deduplicate by ID — collect failures for caller to surface
    seen: set[str] = set()
    items: list[VideoItem] = []
    failures: list[str] = []
    for result in results:
        if isinstance(result, Exception):
            msg = str(result)
            logger.warning("Scraper task failed: %s", msg)
            failures.append(msg)
            continue
        if not result.success:
            msg = f"[{result.platform.value}] {result.error_message}"
            logger.warning("Scraper failure: %s", msg)
            failures.append(msg)
            continue
        for item in result.items:
            if item.id and item.id not in seen:
                seen.add(item.id)
                items.append(item)

    # Surface the first unique failure per platform in the Streamlit UI
    seen_plat_errors: set[str] = set()
    for f in failures:
        key = f[:60]
        if key not in seen_plat_errors:
            seen_plat_errors.add(key)
            st.warning(f"⚠️ Scraper error: {f}")

    logger.info(
        "Total unique items after %d runs × %d platforms: %d",
        runs_per_platform, len(platforms), len(items),
    )
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

            from datetime import datetime, timedelta
            target = settings["max_results"]
            cutoff = datetime.utcnow() - timedelta(days=30)
            MAX_ROUNDS = 5

            seen_ids: set[str] = set()
            all_raw: list[VideoItem] = []
            shown: list[VideoItem] = []
            scrape_error = False

            with st.status(
                f'🔍 Searching for {target} viral videos for "{query}"…',
                expanded=True,
            ) as status:
                for round_num in range(1, MAX_ROUNDS + 1):
                    status.write(f"Round {round_num}/{MAX_ROUNDS} — fetching candidates…")
                    try:
                        batch = _run_scrape(
                            settings_obj=app_settings,
                            query=query,
                            platforms=platforms,
                            max_results=target,
                        )
                    except Exception as exc:
                        st.error(
                            f"Scraping failed: {exc}. "
                            "Check your APIFY_API_TOKEN and network connection."
                        )
                        logger.exception("Scraping error")
                        scrape_error = True
                        break

                    # Accumulate unique items across rounds
                    new_count = 0
                    for item in batch:
                        if item.id and item.id not in seen_ids:
                            seen_ids.add(item.id)
                            all_raw.append(item)
                            new_count += 1

                    # Score everything accumulated so far
                    scorer = ViralityScorer()
                    scored = scorer.score_batch(list(all_raw))

                    # Apply filters
                    passing: list[VideoItem] = []
                    for item in scored:
                        views = item.view_count or item.play_count
                        if item.posted_at is None:
                            continue
                        if item.posted_at.replace(tzinfo=None) < cutoff:
                            continue
                        if views < 40_000:
                            continue
                        if item.follower_count < 10_000:
                            continue
                        passing.append(item)

                    status.write(
                        f"Round {round_num}: {new_count} new unique videos fetched — "
                        f"**{len(passing)}/{target}** qualifying so far."
                    )

                    if len(passing) >= target:
                        shown = passing[:target]
                        status.update(
                            label=f"✅ Found all {target} videos in {round_num} round(s)!",
                            state="complete",
                        )
                        break

                    if new_count == 0:
                        status.write("No new results found — stopping early.")
                        shown = passing[:target]
                        status.update(
                            label=f"⚠️ Found {len(shown)}/{target} — no more unique results available.",
                            state="complete",
                        )
                        break
                else:
                    # Hit MAX_ROUNDS without filling quota
                    shown = passing[:target]
                    status.update(
                        label=f"⚠️ Found {len(shown)}/{target} after {MAX_ROUNDS} rounds — showing best available.",
                        state="complete",
                    )

            if scrape_error:
                _render_tabs(tab_discovery, tab_trends, tab_analytics, settings)
                return

            if not shown:
                st.warning(
                    "No videos matched all filters. Try a broader hashtag or "
                    "lower your Min Virality Score."
                )
                _render_tabs(tab_discovery, tab_trends, tab_analytics, settings)
                return

            st.session_state["items"] = shown
            st.success(
                f"✅ Showing {len(shown)} viral videos "
                f"(from {len(all_raw)} unique candidates across {round_num} round(s))."
            )

    _render_tabs(tab_discovery, tab_trends, tab_analytics, settings)


if __name__ == "__main__":
    main()
