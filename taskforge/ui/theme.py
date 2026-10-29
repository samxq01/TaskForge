"""TaskForge Anthracite Studio-inspired Design System & Theming Engine.

Provides:
- Editorial styling tokens (Anthracite #151515, Charcoal #202020, Warm White #F3F1EB, Lime #D7FF64).
- Injectable CSS stylesheet customized for modern Streamlit elements.
- Unified Matplotlib theme configuring dark editorial aesthetic across all charts.
- Reusable UI component renderers: brand lockup, editorial hero, metric strips, pills, and section headers.
"""

from __future__ import annotations

from typing import Any, Iterable, Optional
import matplotlib as mpl
import matplotlib.pyplot as plt
import streamlit as st


# =============================================================================
# 1. DESIGN TOKENS
# =============================================================================

COLOR_BG = "#121212"                  # Deep canvas background
COLOR_SHELL = "#161616"               # Sidebar and outer panels
COLOR_SURFACE = "#1B1B1B"             # Cards, dialogs, form containers
COLOR_SURFACE_ELEVATED = "#222222"    # Hover states, table headers, active items
COLOR_BORDER = "#2A2A2A"              # Hairline borders
COLOR_BORDER_HOVER = "#3D3D3D"        # Interactive hover borders
COLOR_TEXT_PRIMARY = "#FFFFFF"        # Primary display and body text
COLOR_TEXT_MUTED = "#A6A49E"          # Editorial secondary text, metadata
COLOR_TEXT_TERTIARY = "#6E6D68"       # Disabled, timestamps, minor captions
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
    --tf-bg: #121212;
    --tf-shell: #161616;
    --tf-surface: #1B1B1B;
    --tf-surface-elevated: #222222;
    --tf-border: #2A2A2A;
    --tf-border-hover: #3D3D3D;
    --tf-text-primary: #FFFFFF;
    --tf-text-muted: #A6A49E;
    --tf-text-tertiary: #6E6D68;
    --tf-lime: #D7FF64;
    --tf-warm-white: #F3F1EB;
    --tf-coral: #F87171;
    --tf-amber: #FBBF24;
    --tf-blue: #60A5FA;
    --tf-emerald: #34D399;
}

/* Base Viewport & Body */
html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--tf-bg) !important;
    color: var(--tf-warm-white) !important;
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* Hide default decoration bar */
[data-testid="stDecoration"] {
    background: none !important;
    height: 0px !important;
}

/* Header bar */
[data-testid="stHeader"] {
    background-color: rgba(18, 18, 18, 0.88) !important;
    backdrop-filter: blur(12px) !important;
    border-bottom: 1px solid var(--tf-border) !important;
}

/* Sidebar Shell */
[data-testid="stSidebar"] {
    background-color: var(--tf-shell) !important;
    border-right: 1px solid var(--tf-border) !important;
}

[data-testid="stSidebarUserContent"] {
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
}

/* Main Content Canvas Constraints & Padding */
.main .block-container {
    max-width: 1240px !important;
    padding-top: 1.8rem !important;
    padding-bottom: 4rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}

/* Headings Typography Hierarchy */
h1, h2, h3 {
    font-family: 'Syne', 'Plus Jakarta Sans', sans-serif !important;
    color: var(--tf-text-primary) !important;
    letter-spacing: -0.025em !important;
    font-weight: 700 !important;
}

h4, h5, h6 {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: var(--tf-text-primary) !important;
    letter-spacing: -0.01em !important;
    font-weight: 600 !important;
}

p, span, label, div {
    color: var(--tf-warm-white);
}

/* Custom Editorial Micro-Eyebrows */
.tf-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--tf-lime);
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
    background-color: var(--tf-lime);
    border-radius: 50%;
}

/* Editorial Brand Lockup */
.tf-brand-lockup {
    padding: 0.8rem 0 1.2rem 0;
    border-bottom: 1px solid var(--tf-border);
    margin-bottom: 1.2rem;
}

.tf-brand-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.45rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    color: var(--tf-text-primary);
    line-height: 1.1;
    display: flex;
    align-items: center;
    gap: 0.25rem;
}

.tf-brand-dot {
    color: var(--tf-lime);
    font-weight: 900;
}

.tf-brand-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--tf-text-muted);
    margin-top: 0.25rem;
}

/* Editorial Hero Banner */
.tf-hero {
    background-color: var(--tf-surface);
    border: 1px solid var(--tf-border);
    border-radius: 3px;
    padding: 2.2rem 2.4rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}

.tf-hero::after {
    content: "";
    position: absolute;
    top: 0;
    right: 0;
    width: 220px;
    height: 100%;
    background: radial-gradient(circle at top right, rgba(215, 255, 100, 0.05), transparent 70%);
    pointer-events: none;
}

.tf-hero-headline {
    font-family: 'Syne', sans-serif;
    font-size: 2.25rem;
    font-weight: 800;
    letter-spacing: -0.035em;
    color: var(--tf-text-primary);
    line-height: 1.15;
    margin-bottom: 0.6rem;
}

.tf-hero-subhead {
    font-size: 1.05rem;
    color: var(--tf-text-muted);
    font-weight: 400;
    max-width: 680px;
    line-height: 1.5;
    margin-bottom: 1.2rem;
}

.tf-hero-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 1.2rem;
    align-items: center;
    border-top: 1px solid var(--tf-border);
    padding-top: 1.1rem;
    margin-top: 1.1rem;
}

.tf-hero-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: var(--tf-text-muted);
    display: flex;
    align-items: center;
    gap: 0.4rem;
}

.tf-hero-tag strong {
    color: var(--tf-text-primary);
    font-weight: 600;
}

/* Metric Strip (Restrained Hairline Container) */
.tf-metric-strip {
    display: flex;
    flex-wrap: wrap;
    background-color: var(--tf-border);
    gap: 1px;
    border: 1px solid var(--tf-border);
    border-radius: 3px;
    overflow: hidden;
    margin: 1.4rem 0 2rem 0;
}

.tf-metric-item {
    flex: 1 1 150px;
    background-color: var(--tf-surface);
    padding: 1.1rem 1.3rem;
    transition: background-color 0.15s ease;
}

.tf-metric-item:hover {
    background-color: var(--tf-surface-elevated);
}

.tf-metric-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--tf-text-muted);
    margin-bottom: 0.35rem;
    font-weight: 500;
}

.tf-metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 1.95rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    color: var(--tf-text-primary);
    line-height: 1.1;
}

.tf-metric-caption {
    font-size: 0.72rem;
    color: var(--tf-text-tertiary);
    margin-top: 0.25rem;
    font-family: 'JetBrains Mono', monospace;
}

/* Native Streamlit Metric Overrides */
[data-testid="stMetric"] {
    background-color: var(--tf-surface) !important;
    border: 1px solid var(--tf-border) !important;
    border-radius: 3px !important;
    padding: 0.9rem 1.1rem !important;
    transition: border-color 0.15s ease, background-color 0.15s ease !important;
}

[data-testid="stMetric"]:hover {
    border-color: var(--tf-border-hover) !important;
    background-color: var(--tf-surface-elevated) !important;
}

[data-testid="stMetricLabel"] p {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: var(--tf-text-muted) !important;
    font-weight: 500 !important;
}

[data-testid="stMetricValue"] div {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.85rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.025em !important;
    color: var(--tf-text-primary) !important;
}

/* Buttons - Editorial Anthracite & Lime */
button[kind="primary"], button[data-testid="stBaseButton-primary"] {
    background-color: var(--tf-lime) !important;
    color: #121212 !important;
    border: 1px solid var(--tf-lime) !important;
    border-radius: 3px !important;
    font-weight: 700 !important;
    letter-spacing: -0.01em !important;
    font-size: 0.88rem !important;
    padding: 0.45rem 1.1rem !important;
    box-shadow: none !important;
    transition: background-color 0.15s ease, transform 0.12s ease, box-shadow 0.15s ease !important;
}

button[kind="primary"]:hover, button[data-testid="stBaseButton-primary"]:hover {
    background-color: #c8f550 !important;
    border-color: #c8f550 !important;
    box-shadow: 0 0 16px rgba(215, 255, 100, 0.28) !important;
}

button[kind="secondary"], button[data-testid="stBaseButton-secondary"] {
    background-color: var(--tf-surface) !important;
    color: var(--tf-text-primary) !important;
    border: 1px solid var(--tf-border) !important;
    border-radius: 3px !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
    padding: 0.45rem 1rem !important;
    transition: background-color 0.15s ease, border-color 0.15s ease, color 0.15s ease !important;
}

button[kind="secondary"]:hover, button[data-testid="stBaseButton-secondary"]:hover {
    background-color: var(--tf-surface-elevated) !important;
    border-color: var(--tf-border-hover) !important;
    color: var(--tf-text-primary) !important;
}

/* Radio Navigation Styling in Sidebar */
[data-testid="stSidebar"] [data-testid="stRadio"] > div {
    gap: 0.25rem !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label {
    background-color: transparent !important;
    border: 1px solid transparent !important;
    border-radius: 3px !important;
    padding: 0.45rem 0.65rem !important;
    transition: all 0.15s ease !important;
    cursor: pointer !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background-color: var(--tf-surface) !important;
    border-color: var(--tf-border) !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"] {
    background-color: var(--tf-surface-elevated) !important;
    border-color: rgba(215, 255, 100, 0.35) !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"] p {
    color: var(--tf-lime) !important;
    font-weight: 600 !important;
}

/* Inputs, Selectboxes, Textareas */
input, textarea, [data-baseweb="select"] > div, [data-baseweb="input"] > div {
    background-color: #171717 !important;
    border-color: var(--tf-border) !important;
    border-radius: 3px !important;
    color: var(--tf-text-primary) !important;
    font-size: 0.9rem !important;
}

input:focus, textarea:focus, [data-baseweb="select"]:focus-within > div {
    border-color: var(--tf-lime) !important;
    box-shadow: 0 0 0 1px var(--tf-lime) !important;
}

/* Tabs - Minimalist Editorial Underline */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background-color: transparent !important;
    border-bottom: 1px solid var(--tf-border) !important;
    gap: 1.5rem !important;
    padding: 0.2rem 0 !important;
}

[data-testid="stTabs"] [data-baseweb="tab"] {
    background-color: transparent !important;
    border: none !important;
    color: var(--tf-text-muted) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    padding: 0.65rem 0.2rem !important;
    border-radius: 0 !important;
    transition: color 0.15s ease !important;
}

[data-testid="stTabs"] [data-baseweb="tab"]:hover {
    color: var(--tf-text-primary) !important;
}

[data-testid="stTabs"] [aria-selected="true"] {
    color: var(--tf-lime) !important;
    font-weight: 700 !important;
    border-bottom: 2px solid var(--tf-lime) !important;
}

[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
    background-color: var(--tf-lime) !important;
}

/* Expander - Clean Editorial Container */
[data-testid="stExpander"] {
    background-color: var(--tf-surface) !important;
    border: 1px solid var(--tf-border) !important;
    border-radius: 3px !important;
    margin-bottom: 1rem !important;
}

[data-testid="stExpander"]:hover {
    border-color: var(--tf-border-hover) !important;
}

[data-testid="stExpander"] details summary {
    font-weight: 600 !important;
    color: var(--tf-text-primary) !important;
    font-size: 0.92rem !important;
}

/* Dataframe and Tables */
[data-testid="stDataFrame"], [data-testid="stTable"] {
    border: 1px solid var(--tf-border) !important;
    border-radius: 3px !important;
    overflow: hidden !important;
}

/* Code & Pre Blocks */
code, pre {
    font-family: 'JetBrains Mono', monospace !important;
    background-color: #181818 !important;
    border: 1px solid var(--tf-border) !important;
    color: var(--tf-lime) !important;
    border-radius: 3px !important;
    font-size: 0.84rem !important;
}

/* Editorial Callouts / Cards */
.tf-card {
    background-color: var(--tf-surface);
    border: 1px solid var(--tf-border);
    border-radius: 3px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1.2rem;
    transition: border-color 0.15s ease;
}

.tf-card:hover {
    border-color: var(--tf-border-hover);
}

.tf-card-highlight {
    background-color: #1C1E18;
    border: 1px solid rgba(215, 255, 100, 0.3);
}

.tf-card-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--tf-text-primary);
    margin-bottom: 0.4rem;
}

.tf-card-desc {
    font-size: 0.88rem;
    color: var(--tf-text-muted);
    line-height: 1.5;
}

/* Task Table Row / Action Items */
.tf-task-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 1rem;
    border-bottom: 1px solid var(--tf-border);
    transition: background-color 0.12s ease;
}

.tf-task-row:hover {
    background-color: var(--tf-surface-elevated);
}

/* Editorial Hairline Dividers */
hr {
    border-color: var(--tf-border) !important;
    opacity: 1 !important;
    margin: 1.6rem 0 !important;
}

/* Badges and Semantic Pills */
.tf-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    font-weight: 600;
    padding: 0.2rem 0.55rem;
    border-radius: 2px;
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
    color: #A6A49E;
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
    mpl.rcParams["grid.alpha"] = 0.6
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
    ax.grid(axis="y", linestyle="--", alpha=0.35, color="#2A2A2A")

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
    """Render an editorial hero banner inspired by Anthracite Studio layout."""
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
    sub_html = f'<div style="font-size: 0.9rem; color: #A6A49E; margin-top: 0.2rem; line-height: 1.45;">{subtitle}</div>' if subtitle else ""
    st.markdown(
        f"""
        <div style="margin: 1.8rem 0 0.9rem 0;">
            <div class="tf-eyebrow">{eyebrow}</div>
            <h3 style="margin: 0; font-family: 'Syne', sans-serif; font-size: 1.35rem; font-weight: 700; color: #FFFFFF;">{title}</h3>
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
