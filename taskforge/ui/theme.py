"""TaskForge Anthracite Studio-inspired Design System & Theming Engine.

Provides:
- Editorial styling tokens (Anthracite #0E0E0E, Charcoal #181818, Warm White #F3F1EB, Lime #D7FF64).
- Injectable CSS stylesheet customized for modern Streamlit elements with zero broken text contrast.
- Unified Matplotlib theme configuring dark editorial aesthetic across all charts.
- Reusable UI component renderers: brand lockup, compact editorial hero, pills, and section headers.
"""

from __future__ import annotations

from typing import Any, Optional
import matplotlib as mpl
import streamlit as st


# =============================================================================
# 1. DESIGN TOKENS
# =============================================================================

COLOR_BG = "#0E0E0E"                  # Deep canvas background
COLOR_SHELL = "#141414"               # Sidebar and outer panels
COLOR_SURFACE = "#181818"             # Cards, dialogs, form containers
COLOR_SURFACE_ELEVATED = "#202020"    # Hover states, table headers, active items
COLOR_BORDER = "#262626"              # Hairline borders
COLOR_BORDER_HOVER = "#383838"        # Interactive hover borders
COLOR_TEXT_PRIMARY = "#FFFFFF"        # Primary display and body text
COLOR_TEXT_MUTED = "#9E9E9E"          # Editorial secondary text, metadata
COLOR_TEXT_TERTIARY = "#666666"       # Disabled, timestamps, minor captions
COLOR_LIME = "#D7FF64"                # Signature Anthracite Studio Lime Accent
COLOR_WARM_WHITE = "#F3F1EB"          # High-contrast warm off-white
COLOR_CORAL = "#F87171"               # High risk / blocked / urgent
COLOR_AMBER = "#FBBF24"               # Moderate risk / warning / in-progress
COLOR_BLUE = "#60A5FA"                # Eligible / info / queue items
COLOR_EMERALD = "#34D399"             # Safe / completed / verified


# =============================================================================
# 2. GLOBAL STREAMLIT CSS STYLESHEET
# =============================================================================

ANTHRACITE_CSS = """
<style>
/* Import Editorial Display and Body Typography */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&family=Syne:wght@600;700;800&display=swap');

:root {
    --tf-bg: #0E0E0E;
    --tf-bg-alt: #121212;
    --tf-shell: #141414;
    --tf-surface: #181818;
    --tf-surface-elevated: #202020;
    --tf-border: #262626;
    --tf-border-hover: #383838;
    --tf-text-primary: #FFFFFF;
    --tf-text-muted: #9E9E9E;
    --tf-text-tertiary: #666666;
    --tf-lime: #D7FF64;
    --tf-warm-white: #F3F1EB;
    --tf-coral: #F87171;
    --tf-amber: #FBBF24;
    --tf-blue: #60A5FA;
    --tf-emerald: #34D399;
}

/* Main Content Container Limits & Padding */
.main .block-container {
    max-width: 1200px !important;
    padding-top: 1.5rem !important;
    padding-bottom: 4rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}

/* Headings Typography Hierarchy */
h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
    color: #FFFFFF !important;
    letter-spacing: -0.025em !important;
    font-weight: 700 !important;
}

h4, h5, h6 {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: #FFFFFF !important;
    letter-spacing: -0.01em !important;
    font-weight: 600 !important;
}

/* Custom Editorial Micro-Eyebrows */
.tf-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #D7FF64;
    margin-bottom: 0.35rem;
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
}

.tf-eyebrow::before {
    content: "";
    display: inline-block;
    width: 6px;
    height: 6px;
    background-color: #D7FF64;
    border-radius: 50%;
}

/* Editorial Brand Lockup */
.tf-brand-lockup {
    padding: 0.5rem 0 1rem 0;
    border-bottom: 1px solid #262626;
    margin-bottom: 1rem;
}

.tf-brand-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.45rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    color: #FFFFFF;
    line-height: 1.1;
    display: flex;
    align-items: center;
    gap: 0.2rem;
}

.tf-brand-dot {
    color: #D7FF64;
    font-weight: 900;
}

.tf-brand-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #9E9E9E;
    margin-top: 0.25rem;
}

/* Compact Editorial Hero Banner */
.tf-hero {
    background-color: #141414;
    border: 1px solid #262626;
    border-radius: 6px;
    padding: 1.4rem 1.8rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}

.tf-hero::after {
    content: "";
    position: absolute;
    top: 0;
    right: 0;
    width: 260px;
    height: 100%;
    background: radial-gradient(circle at top right, rgba(215, 255, 100, 0.08), transparent 70%);
    pointer-events: none;
}

.tf-hero-headline {
    font-family: 'Syne', sans-serif;
    font-size: 1.75rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    color: #FFFFFF;
    line-height: 1.2;
    margin-bottom: 0.4rem;
}

.tf-hero-subhead {
    font-size: 0.95rem;
    color: #9E9E9E;
    font-weight: 400;
    max-width: 700px;
    line-height: 1.45;
}

.tf-hero-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 1.2rem;
    align-items: center;
    border-top: 1px solid #222222;
    padding-top: 0.8rem;
    margin-top: 0.9rem;
}

.tf-hero-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: #888888;
    display: flex;
    align-items: center;
    gap: 0.35rem;
}

.tf-hero-tag strong {
    color: #EDEDED;
    font-weight: 600;
}

/* Streamlit Native Metric Overrides for Editorial Look */
[data-testid="stMetric"] {
    background-color: #141414 !important;
    border: 1px solid #242424 !important;
    border-radius: 6px !important;
    padding: 0.85rem 1rem !important;
    transition: border-color 0.15s ease, background-color 0.15s ease !important;
}

[data-testid="stMetric"]:hover {
    border-color: #383838 !important;
    background-color: #181818 !important;
}

[data-testid="stMetricLabel"] p {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: #9E9E9E !important;
    font-weight: 500 !important;
}

[data-testid="stMetricValue"] div {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.8rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.025em !important;
    color: #FFFFFF !important;
}

/* Metric Strips (Hairline Grid) */
.tf-metric-strip {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
    gap: 1px;
    background-color: #242424;
    border: 1px solid #242424;
    border-radius: 6px;
    overflow: hidden;
    margin: 1.2rem 0;
}

.tf-metric-item {
    background-color: #141414;
    padding: 1.1rem 1.3rem;
    transition: background-color 0.15s ease;
}

.tf-metric-item:hover {
    background-color: #181818;
}

.tf-metric-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #9E9E9E;
    margin-bottom: 0.35rem;
}

.tf-metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 1.75rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    color: #FFFFFF;
    line-height: 1.1;
}

.tf-metric-caption {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: #D7FF64;
    margin-top: 0.35rem;
}

/* Buttons - Editorial Anthracite & Lime */
button[kind="primary"], button[data-testid="stBaseButton-primary"] {
    background-color: #D7FF64 !important;
    border: 1px solid #D7FF64 !important;
    border-radius: 4px !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    padding: 0.4rem 1rem !important;
    box-shadow: none !important;
    transition: all 0.15s ease !important;
}

button[kind="primary"] *, button[data-testid="stBaseButton-primary"] * {
    color: #0E0E0E !important;
    font-weight: 700 !important;
}

button[kind="primary"]:hover, button[data-testid="stBaseButton-primary"]:hover {
    background-color: #C8F550 !important;
    border-color: #C8F550 !important;
    box-shadow: 0 0 12px rgba(215, 255, 100, 0.3) !important;
}

button[kind="secondary"], button[data-testid="stBaseButton-secondary"] {
    background-color: #181818 !important;
    border: 1px solid #2E2E2E !important;
    border-radius: 4px !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
    padding: 0.4rem 0.9rem !important;
    transition: all 0.15s ease !important;
}

button[kind="secondary"] *, button[data-testid="stBaseButton-secondary"] * {
    color: #EDEDED !important;
}

button[kind="secondary"]:hover, button[data-testid="stBaseButton-secondary"]:hover {
    background-color: #222222 !important;
    border-color: #444444 !important;
}

/* Sidebar Radio Navigation */
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    border-radius: 4px !important;
    padding: 0.45rem 0.65rem !important;
    transition: background-color 0.12s ease !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background-color: #1A1A1A !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"] {
    background-color: #1F1F1F !important;
    border-left: 2px solid #D7FF64 !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"] p {
    color: #D7FF64 !important;
    font-weight: 600 !important;
}

/* Tabs - Minimalist Editorial Underline */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background-color: transparent !important;
    border-bottom: 1px solid #242424 !important;
    gap: 1.2rem !important;
}

[data-testid="stTabs"] [data-baseweb="tab"] {
    background-color: transparent !important;
    border: none !important;
    color: #9E9E9E !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    padding: 0.6rem 0.2rem !important;
}

[data-testid="stTabs"] [data-baseweb="tab"]:hover {
    color: #FFFFFF !important;
}

[data-testid="stTabs"] [aria-selected="true"] {
    color: #D7FF64 !important;
    font-weight: 700 !important;
}

[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
    background-color: #D7FF64 !important;
}

/* Expander - Clean Dark Box */
[data-testid="stExpander"] {
    background-color: #141414 !important;
    border: 1px solid #242424 !important;
    border-radius: 6px !important;
    margin-bottom: 1rem !important;
}

/* Code & Pre Blocks */
code {
    font-family: 'JetBrains Mono', monospace !important;
    background-color: #181818 !important;
    border: 1px solid #282828 !important;
    color: #D7FF64 !important;
    border-radius: 3px !important;
    padding: 0.15rem 0.4rem !important;
    font-size: 0.84rem !important;
}

/* Task Item Card */
.tf-task-card {
    background-color: #141414;
    border: 1px solid #242424;
    border-radius: 6px;
    padding: 1.1rem 1.4rem;
    margin-bottom: 0.85rem;
    transition: border-color 0.15s ease, background-color 0.15s ease;
}

.tf-task-card:hover {
    border-color: #383838;
    background-color: #171717;
}

/* Badges and Semantic Pills */
.tf-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    font-weight: 600;
    padding: 0.2rem 0.5rem;
    border-radius: 3px;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

.tf-pill-lime {
    background-color: rgba(215, 255, 100, 0.12);
    color: #D7FF64;
    border: 1px solid rgba(215, 255, 100, 0.3);
}

.tf-pill-coral {
    background-color: rgba(248, 113, 113, 0.12);
    color: #F87171;
    border: 1px solid rgba(248, 113, 113, 0.3);
}

.tf-pill-amber {
    background-color: rgba(251, 191, 36, 0.12);
    color: #FBBF24;
    border: 1px solid rgba(251, 191, 36, 0.3);
}

.tf-pill-blue {
    background-color: rgba(96, 165, 250, 0.12);
    color: #60A5FA;
    border: 1px solid rgba(96, 165, 250, 0.3);
}

.tf-pill-muted {
    background-color: rgba(166, 164, 158, 0.1);
    color: #9E9E9E;
    border: 1px solid rgba(166, 164, 158, 0.25);
}

/* Accessibility: Respect Reduced Motion */
@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}
</style>
"""


# =============================================================================
# 3. MATPLOTLIB ANTHRACITE THEME
# =============================================================================

def apply_anthracite_mpl_theme() -> None:
    """Configure global Matplotlib rcParams for cohesive Anthracite visual identity."""
    mpl.rcParams["figure.facecolor"] = COLOR_BG
    mpl.rcParams["axes.facecolor"] = COLOR_SURFACE
    mpl.rcParams["text.color"] = COLOR_TEXT_PRIMARY
    mpl.rcParams["axes.labelcolor"] = COLOR_TEXT_MUTED
    mpl.rcParams["axes.edgecolor"] = COLOR_BORDER
    mpl.rcParams["xtick.color"] = COLOR_TEXT_MUTED
    mpl.rcParams["ytick.color"] = COLOR_TEXT_MUTED
    mpl.rcParams["grid.color"] = "#232323"
    mpl.rcParams["grid.linestyle"] = "--"
    mpl.rcParams["grid.alpha"] = 0.5
    mpl.rcParams["font.sans-serif"] = ["Plus Jakarta Sans", "Inter", "DejaVu Sans", "Arial"]
    mpl.rcParams["font.family"] = "sans-serif"


def style_anthracite_ax(
    ax: mpl.axes.Axes,
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    hide_spines: bool = True,
) -> None:
    """Apply refined Anthracite styling to a Matplotlib axis instance."""
    ax.set_facecolor(COLOR_SURFACE)
    if hide_spines:
        for spine in ["top", "right"]:
            ax.spines[spine].set_visible(False)
        ax.spines["left"].set_color(COLOR_BORDER)
        ax.spines["bottom"].set_color(COLOR_BORDER)
        ax.spines["left"].set_linewidth(0.8)
        ax.spines["bottom"].set_linewidth(0.8)

    ax.tick_params(colors=COLOR_TEXT_MUTED, labelsize=8.5, length=3)
    ax.grid(axis="y", linestyle="--", alpha=0.35, color="#252525")

    if title:
        ax.set_title(title, color=COLOR_TEXT_PRIMARY, fontsize=10.5, fontweight="bold", pad=10)
    if xlabel:
        ax.set_xlabel(xlabel, color=COLOR_TEXT_MUTED, fontsize=9, labelpad=6)
    if ylabel:
        ax.set_ylabel(ylabel, color=COLOR_TEXT_MUTED, fontsize=9, labelpad=6)


# =============================================================================
# 4. REUSABLE UI COMPONENT RENDERERS
# =============================================================================

def inject_anthracite_theme() -> None:
    """Inject the global TaskForge Anthracite stylesheet into the current Streamlit view."""
    st.markdown(ANTHRACITE_CSS, unsafe_allow_html=True)
    apply_anthracite_mpl_theme()


def render_brand_lockup() -> None:
    """Render the official Anthracite-inspired TaskForge brand mark in the sidebar."""
    st.markdown(
        """
        <div class="tf-brand-lockup">
            <div class="tf-brand-title">TASKFORGE<span class="tf-brand-dot">°</span></div>
            <div class="tf-brand-sub">DIGITAL CRAFT &bull; INTELLIGENT PLANNING</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_editorial_hero(
    eyebrow: str,
    headline: str,
    subhead: str,
    meta_tags: Optional[list[tuple[str, str]]] = None,
) -> None:
    """Render a compact editorial hero banner inspired by Anthracite Studio layout."""
    tags_html = ""
    if meta_tags:
        tags_inner = "".join(
            f'<div class="tf-hero-tag"><span>{label}:</span> <strong>{val}</strong></div>'
            for label, val in meta_tags
        )
        tags_html = f'<div class="tf-hero-meta">{tags_inner}</div>'

    html = f"""
    <div class="tf-hero">
        <div class="tf-eyebrow">{eyebrow}</div>
        <div class="tf-hero-headline">{headline}</div>
        <div class="tf-hero-subhead">{subhead}</div>
        {tags_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_section_header(eyebrow: str, title: str, subtitle: Optional[str] = None) -> None:
    """Render a consistent editorial section header."""
    sub_html = f'<div style="font-size: 0.88rem; color: #9E9E9E; margin-top: 0.2rem; line-height: 1.45;">{subtitle}</div>' if subtitle else ""
    st.markdown(
        f"""
        <div style="margin: 1.5rem 0 0.85rem 0;">
            <div class="tf-eyebrow">{eyebrow}</div>
            <h3 style="margin: 0; font-family: 'Syne', sans-serif; font-size: 1.3rem; font-weight: 700; color: #FFFFFF;">{title}</h3>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_strip(metrics: list[dict[str, Any]]) -> None:
    """Render a structured row of metrics separated by hairline borders instead of bulky cards."""
    items_html = ""
    for m in metrics:
        delta_html = f'<div class="tf-metric-caption">{m["caption"]}</div>' if "caption" in m else ""
        items_html += f"""
        <div class="tf-metric-item">
            <div class="tf-metric-label">{m["label"]}</div>
            <div class="tf-metric-value">{m["value"]}</div>
            {delta_html}
        </div>
        """
    st.markdown(f'<div class="tf-metric-strip">{items_html}</div>', unsafe_allow_html=True)


def render_pill(text: str, variant: str = "muted") -> str:
    """Generate HTML for a semantic status or category pill."""
    variant_class = f"tf-pill-{variant}"
    return f'<span class="tf-pill {variant_class}">{text}</span>'
