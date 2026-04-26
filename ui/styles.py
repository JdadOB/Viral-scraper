"""
ui/styles.py — Lavender Design System CSS injection for Viral Scraper.
"""
import streamlit as st


def inject_css() -> None:
    """Inject the full Lavender Design System stylesheet into the Streamlit app."""
    st.markdown(
        """
        <style>
        /* ================================================================
           GLOBAL RESETS & FONT
        ================================================================ */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

        *, *::before, *::after {
            box-sizing: border-box;
        }

        html, body, [class*="css"] {
            font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont,
                         'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            color: #E0E0E0;
        }

        /* ================================================================
           APP BACKGROUND
        ================================================================ */
        .stApp {
            background-color: #1A1A2E !important;
            background-image:
                radial-gradient(ellipse at 20% 50%, rgba(181,126,220,0.04) 0%, transparent 60%),
                radial-gradient(ellipse at 80% 20%, rgba(15,52,96,0.6) 0%, transparent 60%);
            min-height: 100vh;
        }

        /* Main content area */
        .main .block-container {
            background-color: transparent !important;
            padding-top: 2rem;
            padding-bottom: 4rem;
            max-width: 1400px;
        }

        /* ================================================================
           SIDEBAR
        ================================================================ */
        [data-testid="stSidebar"] {
            background-color: #16213E !important;
            border-right: 1px solid rgba(181, 126, 220, 0.2) !important;
        }

        [data-testid="stSidebar"] > div:first-child {
            background-color: #16213E !important;
            padding-top: 1.5rem;
        }

        [data-testid="stSidebar"] .stMarkdown p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] .stTextInput label,
        [data-testid="stSidebar"] .stSelectbox label,
        [data-testid="stSidebar"] .stSlider label,
        [data-testid="stSidebar"] .stNumberInput label,
        [data-testid="stSidebar"] .stCheckbox label {
            color: #A0A0B0 !important;
            font-size: 0.82rem;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }

        /* ================================================================
           HEADINGS
        ================================================================ */
        h1, h2, h3, h4, h5, h6 {
            color: #E0E0E0 !important;
            font-family: 'Inter', system-ui, sans-serif;
        }

        h1 { font-size: 2.2rem; font-weight: 800; }
        h2 { font-size: 1.6rem; font-weight: 700; }
        h3 { font-size: 1.2rem; font-weight: 600; }

        /* ================================================================
           GLASSMORPHIC CARD
        ================================================================ */
        .glass-card {
            background: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(181, 126, 220, 0.3) !important;
            border-radius: 16px !important;
            padding: 1.5rem !important;
            backdrop-filter: blur(10px) !important;
            -webkit-backdrop-filter: blur(10px) !important;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
            transition: all 0.3s ease !important;
            position: relative;
            overflow: hidden;
        }

        .glass-card:hover {
            transform: translateY(-4px) !important;
            box-shadow: 0 16px 48px rgba(181, 126, 220, 0.2) !important;
            border-color: rgba(181, 126, 220, 0.55) !important;
        }

        .glass-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(181,126,220,0.4), transparent);
        }

        /* ================================================================
           METRIC TYPOGRAPHY
        ================================================================ */
        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            color: #B57EDC;
            line-height: 1.1;
            letter-spacing: -0.02em;
        }

        .metric-label {
            font-size: 0.75rem;
            color: #A0A0B0;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-top: 0.25rem;
        }

        .metric-delta-up {
            color: #B57EDC;
            font-size: 0.8rem;
            font-weight: 600;
        }

        .metric-delta-down {
            color: #E94560;
            font-size: 0.8rem;
            font-weight: 600;
        }

        /* ================================================================
           SCORE BADGE
        ================================================================ */
        .score-badge {
            display: inline-block;
            background: linear-gradient(135deg, #B57EDC, #7B2FBE);
            border-radius: 20px;
            padding: 0.25rem 0.75rem;
            font-weight: 700;
            font-size: 0.85rem;
            color: #FFFFFF;
            box-shadow: 0 4px 12px rgba(181, 126, 220, 0.4);
            letter-spacing: 0.02em;
        }

        /* ================================================================
           TREND PILLS
        ================================================================ */
        .trend-pill {
            display: inline-block;
            background: rgba(181, 126, 220, 0.15);
            border: 1px solid rgba(181, 126, 220, 0.4);
            border-radius: 20px;
            padding: 0.25rem 0.6rem;
            margin: 0.2rem;
            font-size: 0.8rem;
            color: #B57EDC;
            cursor: default;
            transition: background 0.2s ease, border-color 0.2s ease;
        }

        .trend-pill:hover {
            background: rgba(181, 126, 220, 0.28);
            border-color: rgba(181, 126, 220, 0.7);
        }

        .hot-badge {
            display: inline-block;
            background: linear-gradient(135deg, #E94560, #C41230);
            border-radius: 20px;
            padding: 0.25rem 0.6rem;
            margin: 0.2rem;
            font-size: 0.8rem;
            color: #FFFFFF;
            font-weight: 600;
            box-shadow: 0 4px 10px rgba(233, 69, 96, 0.35);
        }

        /* ================================================================
           PLATFORM BADGES
        ================================================================ */
        .platform-tiktok {
            color: #69C9D0;
            font-weight: 600;
        }

        .platform-instagram {
            color: #E1306C;
            font-weight: 600;
        }

        .platform-badge-tiktok {
            display: inline-block;
            background: rgba(105, 201, 208, 0.15);
            border: 1px solid rgba(105, 201, 208, 0.4);
            border-radius: 12px;
            padding: 0.15rem 0.55rem;
            font-size: 0.72rem;
            color: #69C9D0;
            font-weight: 600;
            letter-spacing: 0.04em;
        }

        .platform-badge-instagram {
            display: inline-block;
            background: rgba(225, 48, 108, 0.15);
            border: 1px solid rgba(225, 48, 108, 0.4);
            border-radius: 12px;
            padding: 0.15rem 0.55rem;
            font-size: 0.72rem;
            color: #E1306C;
            font-weight: 600;
            letter-spacing: 0.04em;
        }

        /* ================================================================
           VIDEO CARD SPECIFICS
        ================================================================ */
        .video-card-thumb {
            width: 100%;
            height: 180px;
            object-fit: cover;
            border-radius: 10px;
            margin-bottom: 0.75rem;
        }

        .video-card-thumb-placeholder {
            width: 100%;
            height: 180px;
            border-radius: 10px;
            margin-bottom: 0.75rem;
            background: linear-gradient(135deg, #0F3460 0%, #16213E 50%, #1a1a40 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2.5rem;
        }

        .video-card-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 0.5rem;
        }

        .video-card-author {
            font-weight: 600;
            font-size: 0.9rem;
            color: #E0E0E0;
        }

        .video-card-desc {
            font-size: 0.82rem;
            color: #A0A0B0;
            line-height: 1.4;
            margin-bottom: 0.75rem;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }

        .video-card-metrics {
            display: flex;
            gap: 0.75rem;
            flex-wrap: wrap;
            margin-bottom: 0.75rem;
        }

        .video-card-metric {
            display: flex;
            align-items: center;
            gap: 0.2rem;
            font-size: 0.78rem;
            color: #A0A0B0;
        }

        .video-card-metric .metric-num {
            font-weight: 600;
            color: #E0E0E0;
        }

        /* Richey score bar */
        .richey-bar-wrap {
            background: rgba(255, 255, 255, 0.07);
            border-radius: 8px;
            height: 6px;
            width: 100%;
            margin-bottom: 0.75rem;
            overflow: hidden;
        }

        .richey-bar-fill {
            height: 100%;
            border-radius: 8px;
            background: linear-gradient(90deg, #B57EDC, #7B2FBE);
            transition: width 0.6s ease;
        }

        .richey-label {
            font-size: 0.7rem;
            color: #A0A0B0;
            margin-bottom: 0.2rem;
        }

        .video-card-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 0.15rem;
            margin-bottom: 0.75rem;
        }

        .video-card-open-btn {
            display: inline-block;
            background: linear-gradient(135deg, #B57EDC, #7B2FBE);
            color: #FFFFFF !important;
            text-decoration: none !important;
            border-radius: 8px;
            padding: 0.35rem 1rem;
            font-size: 0.82rem;
            font-weight: 600;
            transition: opacity 0.2s ease, transform 0.2s ease;
            letter-spacing: 0.03em;
        }

        .video-card-open-btn:hover {
            opacity: 0.88;
            transform: translateY(-1px);
        }

        /* ================================================================
           CARDS GRID
        ================================================================ */
        .cards-grid {
            display: grid;
            gap: 1.25rem;
        }

        /* ================================================================
           EMPTY STATE
        ================================================================ */
        .empty-state {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 4rem 2rem;
            text-align: center;
        }

        .empty-state-icon {
            font-size: 4rem;
            margin-bottom: 1rem;
            opacity: 0.5;
        }

        .empty-state-title {
            font-size: 1.1rem;
            color: #A0A0B0;
            font-weight: 500;
        }

        /* ================================================================
           STREAMLIT NATIVE COMPONENT OVERRIDES
        ================================================================ */

        /* --- Buttons --- */
        .stButton > button {
            background: linear-gradient(135deg, #B57EDC, #7B2FBE) !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
            padding: 0.5rem 1.5rem !important;
            transition: all 0.2s ease !important;
            box-shadow: 0 4px 14px rgba(181, 126, 220, 0.35) !important;
            letter-spacing: 0.02em;
        }

        .stButton > button:hover {
            background: linear-gradient(135deg, #9B5EC0, #6A25A8) !important;
            box-shadow: 0 6px 20px rgba(181, 126, 220, 0.5) !important;
            transform: translateY(-1px);
        }

        .stButton > button:active {
            transform: translateY(0px);
            box-shadow: 0 2px 8px rgba(181, 126, 220, 0.3) !important;
        }

        /* --- Text Input --- */
        .stTextInput > div > div > input {
            background-color: rgba(15, 52, 96, 0.5) !important;
            border: 1px solid rgba(181, 126, 220, 0.25) !important;
            border-radius: 8px !important;
            color: #E0E0E0 !important;
            font-size: 0.9rem !important;
            transition: border-color 0.2s ease, box-shadow 0.2s ease;
        }

        .stTextInput > div > div > input:focus {
            border-color: #B57EDC !important;
            box-shadow: 0 0 0 2px rgba(181, 126, 220, 0.2) !important;
            outline: none !important;
        }

        .stTextInput > div > div > input::placeholder {
            color: #5A5A7A !important;
        }

        /* --- Selectbox --- */
        .stSelectbox > div > div {
            background-color: rgba(15, 52, 96, 0.5) !important;
            border: 1px solid rgba(181, 126, 220, 0.25) !important;
            border-radius: 8px !important;
            color: #E0E0E0 !important;
        }

        .stSelectbox > div > div:focus-within {
            border-color: #B57EDC !important;
            box-shadow: 0 0 0 2px rgba(181, 126, 220, 0.2) !important;
        }

        [data-baseweb="select"] {
            background-color: rgba(15, 52, 96, 0.5) !important;
        }

        [data-baseweb="select"] > div {
            background-color: rgba(15, 52, 96, 0.5) !important;
            border: 1px solid rgba(181, 126, 220, 0.25) !important;
            border-radius: 8px !important;
            color: #E0E0E0 !important;
        }

        [data-baseweb="popover"] {
            background-color: #16213E !important;
            border: 1px solid rgba(181, 126, 220, 0.3) !important;
            border-radius: 8px !important;
        }

        [data-baseweb="menu"] {
            background-color: #16213E !important;
        }

        [data-baseweb="option"] {
            background-color: #16213E !important;
            color: #E0E0E0 !important;
        }

        [data-baseweb="option"]:hover {
            background-color: rgba(181, 126, 220, 0.15) !important;
        }

        /* --- Slider --- */
        .stSlider > div > div > div > div {
            background: linear-gradient(90deg, #B57EDC, #7B2FBE) !important;
        }

        .stSlider > div > div > div > div > div {
            background-color: #B57EDC !important;
            border: 2px solid #E0E0E0 !important;
            box-shadow: 0 2px 8px rgba(181, 126, 220, 0.5) !important;
        }

        /* --- Number Input --- */
        .stNumberInput > div > div > input {
            background-color: rgba(15, 52, 96, 0.5) !important;
            border: 1px solid rgba(181, 126, 220, 0.25) !important;
            border-radius: 8px !important;
            color: #E0E0E0 !important;
        }

        .stNumberInput > div > div > input:focus {
            border-color: #B57EDC !important;
            box-shadow: 0 0 0 2px rgba(181, 126, 220, 0.2) !important;
        }

        /* --- Checkbox --- */
        .stCheckbox > label {
            color: #E0E0E0 !important;
        }

        .stCheckbox > label > div > div {
            background-color: rgba(15, 52, 96, 0.5) !important;
            border: 1px solid rgba(181, 126, 220, 0.4) !important;
            border-radius: 4px !important;
        }

        /* --- st.metric overrides --- */
        [data-testid="metric-container"] {
            background: rgba(255, 255, 255, 0.04) !important;
            border: 1px solid rgba(181, 126, 220, 0.2) !important;
            border-radius: 12px !important;
            padding: 1rem !important;
        }

        [data-testid="metric-container"] [data-testid="stMetricValue"] {
            color: #B57EDC !important;
            font-size: 1.8rem !important;
            font-weight: 700 !important;
        }

        [data-testid="metric-container"] [data-testid="stMetricLabel"] {
            color: #A0A0B0 !important;
            font-size: 0.75rem !important;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }

        [data-testid="metric-container"] [data-testid="stMetricDelta"] {
            color: #B57EDC !important;
            font-size: 0.8rem !important;
            font-weight: 600 !important;
        }

        [data-testid="metric-container"] [data-testid="stMetricDelta"][data-direction="negative"] {
            color: #E94560 !important;
        }

        /* --- Tabs --- */
        .stTabs [data-baseweb="tab-list"] {
            background-color: rgba(22, 33, 62, 0.8) !important;
            border-radius: 12px !important;
            padding: 0.3rem !important;
            border: 1px solid rgba(181, 126, 220, 0.15) !important;
            gap: 0.2rem;
        }

        .stTabs [data-baseweb="tab"] {
            background-color: transparent !important;
            color: #A0A0B0 !important;
            border-radius: 8px !important;
            font-weight: 500 !important;
            transition: all 0.2s ease !important;
            border: none !important;
        }

        .stTabs [data-baseweb="tab"]:hover {
            color: #E0E0E0 !important;
            background-color: rgba(181, 126, 220, 0.1) !important;
        }

        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, rgba(181,126,220,0.25), rgba(123,47,190,0.2)) !important;
            color: #B57EDC !important;
            font-weight: 600 !important;
        }

        .stTabs [data-baseweb="tab-highlight"] {
            background-color: transparent !important;
        }

        .stTabs [data-baseweb="tab-border"] {
            display: none !important;
        }

        /* --- Divider --- */
        hr {
            border-color: rgba(181, 126, 220, 0.15) !important;
        }

        /* --- Expander --- */
        .streamlit-expanderHeader {
            background-color: rgba(15, 52, 96, 0.4) !important;
            border: 1px solid rgba(181, 126, 220, 0.2) !important;
            border-radius: 8px !important;
            color: #E0E0E0 !important;
        }

        .streamlit-expanderContent {
            background-color: rgba(15, 52, 96, 0.2) !important;
            border: 1px solid rgba(181, 126, 220, 0.15) !important;
            border-top: none !important;
            border-radius: 0 0 8px 8px !important;
        }

        /* --- Spinner / progress --- */
        .stSpinner > div {
            border-top-color: #B57EDC !important;
        }

        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, #B57EDC, #7B2FBE) !important;
        }

        /* --- Success / Error / Warning messages --- */
        .stSuccess {
            background-color: rgba(181, 126, 220, 0.12) !important;
            border: 1px solid rgba(181, 126, 220, 0.4) !important;
            border-radius: 8px !important;
            color: #E0E0E0 !important;
        }

        .stError {
            background-color: rgba(233, 69, 96, 0.12) !important;
            border: 1px solid rgba(233, 69, 96, 0.4) !important;
            border-radius: 8px !important;
        }

        .stWarning {
            background-color: rgba(255, 180, 0, 0.08) !important;
            border: 1px solid rgba(255, 180, 0, 0.3) !important;
            border-radius: 8px !important;
        }

        /* --- Dataframe / Table --- */
        .stDataFrame {
            border: 1px solid rgba(181, 126, 220, 0.2) !important;
            border-radius: 12px !important;
            overflow: hidden;
        }

        /* ================================================================
           CUSTOM SCROLLBAR
        ================================================================ */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }

        ::-webkit-scrollbar-track {
            background: #1A1A2E;
        }

        ::-webkit-scrollbar-thumb {
            background: #B57EDC;
            border-radius: 3px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #9B5EC0;
        }

        * {
            scrollbar-width: thin;
            scrollbar-color: #B57EDC #1A1A2E;
        }

        /* ================================================================
           HERO / WELCOME SECTION
        ================================================================ */
        .hero-title {
            font-size: 3.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #B57EDC 0%, #E94560 50%, #B57EDC 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-align: center;
            line-height: 1.15;
            margin-bottom: 0.75rem;
        }

        .hero-subtitle {
            font-size: 1.1rem;
            color: #A0A0B0;
            text-align: center;
            margin-bottom: 2.5rem;
        }

        .hero-feature-icon {
            font-size: 2.5rem;
            margin-bottom: 0.75rem;
            display: block;
        }

        .hero-feature-title {
            font-size: 1rem;
            font-weight: 700;
            color: #E0E0E0;
            margin-bottom: 0.4rem;
        }

        .hero-feature-desc {
            font-size: 0.85rem;
            color: #A0A0B0;
            line-height: 1.5;
        }

        /* ================================================================
           GRADIENT TITLE
        ================================================================ */
        .gradient-title {
            background: linear-gradient(135deg, #B57EDC 0%, #9B5EC0 40%, #E94560 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 2.4rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            line-height: 1.2;
        }

        /* ================================================================
           SECTION HEADERS
        ================================================================ */
        .section-header {
            font-size: 0.72rem;
            font-weight: 700;
            color: #B57EDC;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            margin-bottom: 0.6rem;
            margin-top: 1.2rem;
            padding-bottom: 0.3rem;
            border-bottom: 1px solid rgba(181, 126, 220, 0.2);
        }

        /* ================================================================
           SOUND TREND TABLE
        ================================================================ */
        .sound-row {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.5rem 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }

        .sound-name {
            flex: 1;
            font-size: 0.85rem;
            color: #E0E0E0;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .sound-count {
            font-size: 0.78rem;
            color: #B57EDC;
            font-weight: 600;
            min-width: 2.5rem;
            text-align: right;
        }

        .sound-virality-bar {
            width: 80px;
            height: 5px;
            background: rgba(255,255,255,0.07);
            border-radius: 4px;
            overflow: hidden;
        }

        .sound-virality-fill {
            height: 100%;
            background: linear-gradient(90deg, #B57EDC, #E94560);
            border-radius: 4px;
        }

        /* ================================================================
           LOGO / BRAND
        ================================================================ */
        .brand-logo {
            font-size: 1.6rem;
            font-weight: 800;
            background: linear-gradient(135deg, #B57EDC, #9B5EC0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: -0.01em;
        }

        .powered-by {
            font-size: 0.7rem;
            color: #5A5A7A;
            text-align: center;
            letter-spacing: 0.06em;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
