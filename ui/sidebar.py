"""
ui/sidebar.py — Sidebar renderer for Viral Scraper.
Returns a settings dict consumed by the main app.
"""
from __future__ import annotations

import streamlit as st


def render_sidebar() -> dict:
    """Render the left sidebar and return a settings dictionary.

    Returns
    -------
    dict with keys:
        platforms   : list[str]   — e.g. ["tiktok", "instagram"]
        query       : str         — hashtag / keyword entered by the user
        scrape_clicked : bool     — True when the "Scrape Now" button is pressed
        min_virality   : int      — 0–100
        min_richey     : float    — 0.0–1.0
        sort_by        : str
        max_results    : int
        card_cols      : int
        richey_only    : bool
    """
    with st.sidebar:
        # ------------------------------------------------------------------ #
        # Logo / Brand
        # ------------------------------------------------------------------ #
        st.markdown(
            """
            <div style="text-align:center;padding:0.5rem 0 1.2rem;">
              <div class="brand-logo">🔮 Viral Scraper</div>
              <div style="font-size:0.72rem;color:#A0A0B0;margin-top:0.3rem;
                          letter-spacing:0.06em;">
                Real-time viral content intelligence
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        # ------------------------------------------------------------------ #
        # Section: Platforms
        # ------------------------------------------------------------------ #
        st.markdown('<div class="section-header">Platforms</div>', unsafe_allow_html=True)

        col_tt, col_ig = st.columns(2)
        with col_tt:
            use_tiktok = st.checkbox(
                "TikTok",
                value=True,
                key="chk_tiktok",
                help="Scrape TikTok for this query",
            )
        with col_ig:
            use_instagram = st.checkbox(
                "Instagram",
                value=True,
                key="chk_instagram",
                help="Scrape Instagram Reels for this query",
            )

        platforms: list[str] = []
        if use_tiktok:
            platforms.append("tiktok")
        if use_instagram:
            platforms.append("instagram")

        # ------------------------------------------------------------------ #
        # Section: Search
        # ------------------------------------------------------------------ #
        st.markdown('<div class="section-header">Search</div>', unsafe_allow_html=True)

        query = st.text_input(
            "Hashtag / Keyword",
            value="",
            placeholder="#trending  or  aesthetic",
            key="search_query",
            label_visibility="collapsed",
        )

        scrape_clicked = st.button(
            "🚀 Scrape Now",
            use_container_width=True,
            key="btn_scrape",
        )

        # ------------------------------------------------------------------ #
        # Section: Filters
        # ------------------------------------------------------------------ #
        st.markdown('<div class="section-header">Filters</div>', unsafe_allow_html=True)

        min_virality = st.slider(
            "Min Virality Score",
            min_value=0,
            max_value=100,
            value=0,
            step=1,
            key="slider_virality",
            help="Only show videos with a virality score at or above this threshold.",
        )

        sort_by = st.selectbox(
            "Sort By",
            options=["Virality Score", "Views", "Likes", "Recent"],
            index=0,
            key="select_sort",
        )

        max_results = st.number_input(
            "Max Results",
            min_value=10,
            max_value=200,
            value=50,
            step=10,
            key="num_max_results",
        )

        # ------------------------------------------------------------------ #
        # Section: Display
        # ------------------------------------------------------------------ #
        st.markdown('<div class="section-header">Display</div>', unsafe_allow_html=True)

        card_cols = st.selectbox(
            "Card Columns",
            options=[2, 3, 4],
            index=1,
            key="select_card_cols",
        )

        # ------------------------------------------------------------------ #
        # Footer
        # ------------------------------------------------------------------ #
        st.divider()
        st.markdown(
            '<div class="powered-by">Powered by Apify + Claude</div>',
            unsafe_allow_html=True,
        )

    return {
        "platforms": platforms,
        "query": query.strip(),
        "scrape_clicked": scrape_clicked,
        "min_virality": int(min_virality),
        "sort_by": sort_by,
        "max_results": int(max_results),
        "card_cols": int(card_cols),
    }
