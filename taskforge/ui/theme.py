"""TaskForge Potadot-Inspired Design System & Theming Engine.

Provides:
- Design tokens inspired by Potadot (Clean Light Canvas #F8FAFC, Card Surface #FFFFFF,
  Deep Slate #0F172A, Digital Blue #2563EB, Semantic Badges).
- Unified CSS stylesheet for Streamlit with high-contrast, accessible typography.
- Professional Matplotlib theme for clean, high-resolution charts in light mode.
- Reusable UI component renderers: brand lockup with dot motif, product hero,
  metric strips, semantic pills, section headers, and interactive module preview cards.
"""

from __future__ import annotations

from typing import Any, Optional
import matplotlib as mpl
import streamlit as st


# =============================================================================
# 1. DESIGN TOKENS
# =============================================================================

COLOR_BG = "#F8FAFC"                  # Crisp modern light canvas (Slate 50)
COLOR_SHELL = "#FFFFFF"               # Sidebar and outer panels
COLOR_SURFACE = "#FFFFFF"             # Cards, dialogs, form containers
COLOR_SURFACE_ELEVATED = "#F1F5F9"    # Hover states, table headers, active items (Slate 100)
COLOR_BORDER = "#E2E8F0"              # Subtle hairline borders (Slate 200)
COLOR_BORDER_HOVER = "#CBD5E1"        # Interactive hover borders (Slate 300)
COLOR_TEXT_PRIMARY = "#0F172A"        # Deep slate primary display & body text (Slate 900)
COLOR_TEXT_MUTED = "#475569"          # Secondary text, metadata, descriptions (Slate 600)
COLOR_TEXT_TERTIARY = "#94A3B8"       # Disabled, timestamps, minor captions (Slate 400)
COLOR_BRAND = "#2563EB"               # Signature Potadot Digital Blue (Blue 600)
COLOR_BRAND_HOVER = "#1D4ED8"         # Blue hover state (Blue 700)
COLOR_BRAND_LIGHT = "#EFF6FF"         # Soft blue tint for tags & highlights (Blue 50)

# Semantic Colors
COLOR_CORAL = "#EF4444"               # High risk / blocked / urgent / overdue (Red 500)
COLOR_AMBER = "#F59E0B"               # Warning / in-progress / moderate risk (Amber 500)
COLOR_BLUE = "#3B82F6"                # Eligible / info / queue items (Blue 500)
COLOR_EMERALD = "#10B981"             # Safe / completed / verified (Emerald 500)
COLOR_LIME = "#2563EB"                # Backwards-compatibility alias (maps to Potadot Brand Blue)


# =============================================================================
# 2. GLOBAL STREAMLIT CSS STYLESHEET
# =============================================================================

POTADOT_CSS = """
<style>
/* Import Contemporary Product Typography */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&family=Syne:wght@600;700;800&display=swap');

:root {
    --pt-bg: #F8FAFC;
    --pt-shell: #FFFFFF;
    --pt-surface: #FFFFFF;
    --pt-surface-elevated: #F1F5F9;
    --pt-border: #E2E8F0;
    --pt-border-hover: #CBD5E1;
    --pt-text-primary: #0F172A;
    --pt-text-muted: #475569;
    --pt-text-tertiary: #94A3B8;
    --pt-brand: #2563EB;
    --pt-brand-hover: #1D4ED8;
    --pt-brand-light: #EFF6FF;
    --pt-coral: #EF4444;
    --pt-amber: #F59E0B;
    --pt-blue: #3B82F6;
    --pt-emerald: #10B981;
    /* Legacy fallback tokens */
    --tf-bg: #F8FAFC;
    --tf-shell: #FFFFFF;
    --tf-surface: #FFFFFF;
    --tf-border: #E2E8F0;
    --tf-lime: #2563EB;
    --tf-text-primary: #0F172A;
    --tf-text-muted: #475569;
}

/* Base Viewport & Body */
html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--pt-bg) !important;
    color: var(--pt-text-primary) !important;
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* Main Content Container Limits & Padding */
.main .block-container {
    max-width: 1240px !important;
    padding-top: 1.5rem !important;
    padding-bottom: 4rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}

/* Hide default decoration bar */
[data-testid="stDecoration"] {
    background: none !important;
    height: 0px !important;
}

/* Header bar */
[data-testid="stHeader"] {
    background-color: rgba(255, 255, 255, 0.92) !important;
    backdrop-filter: blur(12px) !important;
    border-bottom: 1px solid var(--pt-border) !important;
}

/* Sidebar Shell */
[data-testid="stSidebar"] {
    background-color: var(--pt-shell) !important;
    border-right: 1px solid var(--pt-border) !important;
}

[data-testid="stSidebarUserContent"] {
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
}

/* Headings Typography Hierarchy */
h1, h2, h3 {
    font-family: 'Syne', 'Plus Jakarta Sans', sans-serif !important;
    color: var(--pt-text-primary) !important;
    letter-spacing: -0.025em !important;
    font-weight: 700 !important;
}

h4, h5, h6 {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: var(--pt-text-primary) !important;
    letter-spacing: -0.01em !important;
    font-weight: 600 !important;
}

/* Custom Potadot Eyebrow with Dot Motif */
.pt-eyebrow, .tf-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--pt-brand);
    margin-bottom: 0.35rem;
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
}

.pt-eyebrow::before, .tf-eyebrow::before {
    content: "";
    display: inline-block;
    width: 7px;
    height: 7px;
    background-color: var(--pt-brand);
    border-radius: 50%;
    box-shadow: 0 0 6px rgba(37, 99, 235, 0.4);
}

/* Potadot Brand Lockup */
.pt-brand-lockup, .tf-brand-lockup {
    padding: 0.4rem 0 1rem 0;
    border-bottom: 1px solid var(--pt-border);
    margin-bottom: 1.1rem;
}

.pt-brand-title, .tf-brand-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.45rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    color: var(--pt-text-primary);
    line-height: 1.1;
    display: flex;
    align-items: center;
    gap: 0.25rem;
}

.pt-brand-dot, .tf-brand-dot {
    color: var(--pt-brand);
    font-weight: 900;
    font-size: 1.4rem;
    line-height: 0;
}

.pt-brand-sub, .tf-brand-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--pt-text-muted);
    margin-top: 0.35rem;
}

/* Editorial Product Hero Banner */
.pt-hero, .tf-hero {
    background-color: #FFFFFF;
    border: 1px solid var(--pt-border);
    border-radius: 10px;
    padding: 1.6rem 2rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.04), 0 1px 2px -1px rgba(0, 0, 0, 0.02);
}

.pt-hero::after, .tf-hero::after {
    content: "";
    position: absolute;
    top: 0;
    right: 0;
    width: 280px;
    height: 100%;
    background: radial-gradient(circle at top right, rgba(37, 99, 235, 0.08), transparent 70%);
    pointer-events: none;
}

.pt-hero-headline, .tf-hero-headline {
    font-family: 'Syne', sans-serif;
    font-size: 1.85rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    color: var(--pt-text-primary);
    line-height: 1.2;
    margin-bottom: 0.45rem;
}

.pt-hero-subhead, .tf-hero-subhead {
    font-size: 0.95rem;
    color: var(--pt-text-muted);
    font-weight: 400;
    max-width: 720px;
    line-height: 1.5;
}

.pt-hero-meta, .tf-hero-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    align-items: center;
    border-top: 1px solid #F1F5F9;
    padding-top: 0.85rem;
    margin-top: 1rem;
}

.pt-hero-tag, .tf-hero-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: var(--pt-text-muted);
    background-color: #F8FAFC;
    border: 1px solid var(--pt-border);
    border-radius: 4px;
    padding: 0.25rem 0.6rem;
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
}

.pt-hero-tag strong, .tf-hero-tag strong {
    color: var(--pt-brand);
    font-weight: 600;
}

/* Metric Strips (Hairline Grid on Clean White) */
.pt-metric-strip, .tf-metric-strip {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
    gap: 1px;
    background-color: var(--pt-border);
    border: 1px solid var(--pt-border);
    border-radius: 8px;
    overflow: hidden;
    margin: 1.2rem 0;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.03);
}

.pt-metric-item, .tf-metric-item {
    background-color: #FFFFFF;
    padding: 1.1rem 1.3rem;
    transition: background-color 0.15s ease;
}

.pt-metric-item:hover, .tf-metric-item:hover {
    background-color: #F8FAFC;
}

.pt-metric-label, .tf-metric-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--pt-text-muted);
    margin-bottom: 0.35rem;
}

.pt-metric-value, .tf-metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 1.75rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    color: var(--pt-text-primary);
    line-height: 1.1;
}

.pt-metric-caption, .tf-metric-caption {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: var(--pt-brand);
    margin-top: 0.35rem;
    font-weight: 500;
}

/* Streamlit Native Metric Overrides for Potadot Look */
[data-testid="stMetric"] {
    background-color: #FFFFFF !important;
    border: 1px solid var(--pt-border) !important;
    border-radius: 8px !important;
    padding: 0.9rem 1.1rem !important;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.04) !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
}

[data-testid="stMetric"]:hover {
    border-color: var(--pt-border-hover) !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
}

[data-testid="stMetricLabel"] p {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: var(--pt-text-muted) !important;
    font-weight: 600 !important;
}

[data-testid="stMetricValue"] div {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.8rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.025em !important;
    color: var(--pt-text-primary) !important;
}

/* Primary and Secondary Buttons */
button[kind="primary"], button[data-testid="stBaseButton-primary"] {
    background-color: var(--pt-brand) !important;
    border: 1px solid var(--pt-brand) !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 0.45rem 1.1rem !important;
    box-shadow: 0 1px 2px 0 rgba(37, 99, 235, 0.2) !important;
    transition: all 0.15s ease !important;
}

button[kind="primary"] *, button[data-testid="stBaseButton-primary"] * {
    color: #FFFFFF !important;
    font-weight: 600 !important;
}

button[kind="primary"]:hover, button[data-testid="stBaseButton-primary"]:hover {
    background-color: var(--pt-brand-hover) !important;
    border-color: var(--pt-brand-hover) !important;
    box-shadow: 0 4px 8px 0 rgba(37, 99, 235, 0.25) !important;
}

button[kind="secondary"], button[data-testid="stBaseButton-secondary"] {
    background-color: #FFFFFF !important;
    border: 1px solid var(--pt-border) !important;
    border-radius: 6px !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
    padding: 0.45rem 1rem !important;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.03) !important;
    transition: all 0.15s ease !important;
}

button[kind="secondary"] *, button[data-testid="stBaseButton-secondary"] * {
    color: var(--pt-text-primary) !important;
    font-weight: 500 !important;
}

button[kind="secondary"]:hover, button[data-testid="stBaseButton-secondary"]:hover {
    background-color: #F8FAFC !important;
    border-color: var(--pt-border-hover) !important;
    color: var(--pt-brand) !important;
}

/* Sidebar Radio Navigation */
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    border-radius: 6px !important;
    padding: 0.45rem 0.75rem !important;
    margin-bottom: 0.2rem !important;
    transition: background-color 0.12s ease !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background-color: #F1F5F9 !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"] {
    background-color: var(--pt-brand-light) !important;
    border-left: 3px solid var(--pt-brand) !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"] p {
    color: var(--pt-brand) !important;
    font-weight: 600 !important;
}

/* Tabs - Minimalist Editorial Underline */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background-color: transparent !important;
    border-bottom: 1px solid var(--pt-border) !important;
    gap: 1.4rem !important;
}

[data-testid="stTabs"] [data-baseweb="tab"] {
    background-color: transparent !important;
    border: none !important;
    color: var(--pt-text-muted) !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    padding: 0.65rem 0.2rem !important;
}

[data-testid="stTabs"] [data-baseweb="tab"]:hover {
    color: var(--pt-brand) !important;
}

[data-testid="stTabs"] [aria-selected="true"] {
    color: var(--pt-brand) !important;
    font-weight: 700 !important;
}

[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
    background-color: var(--pt-brand) !important;
    height: 2px !important;
}

/* Expander & Bordered Containers */
[data-testid="stExpander"] {
    background-color: #FFFFFF !important;
    border: 1px solid var(--pt-border) !important;
    border-radius: 8px !important;
    margin-bottom: 1rem !important;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.03) !important;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #FFFFFF !important;
    border: 1px solid var(--pt-border) !important;
    border-radius: 8px !important;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.03) !important;
}

/* Form inputs & controls */
input[type="text"], input[type="number"], textarea, select {
    background-color: #FFFFFF !important;
    border: 1px solid var(--pt-border) !important;
    border-radius: 6px !important;
    color: var(--pt-text-primary) !important;
}

input:focus, textarea:focus {
    border-color: var(--pt-brand) !important;
    box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.15) !important;
}

/* Code & Pre Blocks */
code {
    font-family: 'JetBrains Mono', monospace !important;
    background-color: #F1F5F9 !important;
    border: 1px solid #E2E8F0 !important;
    color: var(--pt-brand) !important;
    border-radius: 4px !important;
    padding: 0.15rem 0.4rem !important;
    font-size: 0.84rem !important;
}

/* Hairline Dividers */
hr {
    border-color: var(--pt-border) !important;
    opacity: 1 !important;
    margin: 1.5rem 0 !important;
}

/* Badges and Semantic Pills */
.tf-pill, .pt-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    font-weight: 600;
    padding: 0.22rem 0.55rem;
    border-radius: 4px;
    letter-spacing: 0.03em;
    text-transform: uppercase;
}

.tf-pill-lime, .pt-pill-completed {
    background-color: #ECFDF5;
    color: #047857;
    border: 1px solid #A7F3D0;
}

.tf-pill-blue, .pt-pill-in-progress {
    background-color: #EFF6FF;
    color: #1D4ED8;
    border: 1px solid #BFDBFE;
}

.tf-pill-coral, .pt-pill-urgent {
    background-color: #FEF2F2;
    color: #B91C1C;
    border: 1px solid #FECACA;
}

.tf-pill-amber, .pt-pill-warning {
    background-color: #FFFBEB;
    color: #B45309;
    border: 1px solid #FDE68A;
}

.tf-pill-muted, .pt-pill-muted {
    background-color: #F1F5F9;
    color: #475569;
    border: 1px solid #E2E8F0;
}

/* Product Showcase Cards */
.pt-preview-card {
    background-color: #FFFFFF;
    border: 1px solid var(--pt-border);
    border-radius: 8px;
    padding: 1.3rem 1.4rem;
    margin-bottom: 0.9rem;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.04);
    transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
}

.pt-preview-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.07);
    border-color: var(--pt-border-hover);
}

.pt-preview-number {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    font-weight: 700;
    color: var(--pt-brand);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 0.35rem;
}

.pt-preview-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--pt-text-primary);
    margin-bottom: 0.3rem;
}

.pt-preview-desc {
    font-size: 0.86rem;
    color: var(--pt-text-muted);
    line-height: 1.5;
    margin-bottom: 0.8rem;
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

# Alias for backwards compatibility with tests and existing imports
ANTHRACITE_CSS = POTADOT_CSS


# =============================================================================
# 3. MATPLOTLIB POTADOT THEME (LIGHT MODE)
# =============================================================================

def apply_potadot_mpl_theme() -> None:
    """Configure global Matplotlib rcParams for clean light product visual identity."""
    mpl.rcParams["figure.facecolor"] = "#FFFFFF"
    mpl.rcParams["axes.facecolor"] = "#FFFFFF"
    mpl.rcParams["text.color"] = COLOR_TEXT_PRIMARY
    mpl.rcParams["axes.labelcolor"] = COLOR_TEXT_MUTED
    mpl.rcParams["axes.edgecolor"] = COLOR_BORDER
    mpl.rcParams["xtick.color"] = COLOR_TEXT_MUTED
    mpl.rcParams["ytick.color"] = COLOR_TEXT_MUTED
    mpl.rcParams["grid.color"] = "#F1F5F9"
    mpl.rcParams["grid.linestyle"] = "--"
    mpl.rcParams["grid.alpha"] = 0.8
    mpl.rcParams["font.sans-serif"] = ["Plus Jakarta Sans", "Inter", "DejaVu Sans", "Arial"]
    mpl.rcParams["font.family"] = "sans-serif"


# Alias for backwards compatibility
apply_anthracite_mpl_theme = apply_potadot_mpl_theme


def style_potadot_ax(
    ax: mpl.axes.Axes,
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    hide_spines: bool = True,
) -> None:
    """Apply refined Potadot light product styling to a Matplotlib axis instance."""
    ax.set_facecolor("#FFFFFF")
    if hide_spines:
        for spine in ["top", "right"]:
            ax.spines[spine].set_visible(False)
        ax.spines["left"].set_color(COLOR_BORDER)
        ax.spines["bottom"].set_color(COLOR_BORDER)
        ax.spines["left"].set_linewidth(1.0)
        ax.spines["bottom"].set_linewidth(1.0)

    ax.tick_params(colors=COLOR_TEXT_MUTED, labelsize=8.5, length=3)
    ax.grid(axis="y", linestyle="--", alpha=0.8, color="#F1F5F9")

    if title:
        ax.set_title(title, color=COLOR_TEXT_PRIMARY, fontsize=10.5, fontweight="bold", pad=10)
    if xlabel:
        ax.set_xlabel(xlabel, color=COLOR_TEXT_MUTED, fontsize=9, labelpad=6)
    if ylabel:
        ax.set_ylabel(ylabel, color=COLOR_TEXT_MUTED, fontsize=9, labelpad=6)


# Alias for backwards compatibility
style_anthracite_ax = style_potadot_ax


# =============================================================================
# 4. REUSABLE UI COMPONENT RENDERERS
# =============================================================================

def inject_potadot_theme() -> None:
    """Inject the global TaskForge Potadot stylesheet into the current Streamlit view."""
    st.markdown(POTADOT_CSS, unsafe_allow_html=True)
    apply_potadot_mpl_theme()


# Alias for backwards compatibility
inject_anthracite_theme = inject_potadot_theme


def render_brand_lockup() -> None:
    """Render the official Potadot-inspired TaskForge brand mark in the sidebar."""
    st.markdown(
        """
        <div class="pt-brand-lockup">
            <div class="pt-brand-title">TaskForge<span class="pt-brand-dot">•</span></div>
            <div class="pt-brand-sub">INTELLIGENT TASK MANAGEMENT</div>
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
    """Render an editorial product hero banner inspired by Potadot's clean product presentation."""
    tags_html = ""
    if meta_tags:
        tags_inner = "".join(
            f'<div class="pt-hero-tag"><span>{label}:</span> <strong>{val}</strong></div>'
            for label, val in meta_tags
        )
        tags_html = f'<div class="pt-hero-meta">{tags_inner}</div>'

    html = f"""
    <div class="pt-hero">
        <div class="pt-eyebrow">{eyebrow}</div>
        <div class="pt-hero-headline">{headline}</div>
        <div class="pt-hero-subhead">{subhead}</div>
        {tags_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_section_header(eyebrow: str, title: str, subtitle: Optional[str] = None) -> None:
    """Render a consistent product section header with dot motif."""
    sub_html = f'<div style="font-size: 0.88rem; color: #475569; margin-top: 0.2rem; line-height: 1.45;">{subtitle}</div>' if subtitle else ""
    st.markdown(
        f"""
        <div style="margin: 1.4rem 0 0.85rem 0;">
            <div class="pt-eyebrow">{eyebrow}</div>
            <h3 style="margin: 0; font-family: 'Syne', sans-serif; font-size: 1.35rem; font-weight: 700; color: #0F172A;">{title}</h3>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_strip(metrics: list[dict[str, Any]]) -> None:
    """Render a structured row of metrics separated by hairline borders on clean white cards."""
    items_html = ""
    for m in metrics:
        delta_html = f'<div class="pt-metric-caption">{m["caption"]}</div>' if "caption" in m else ""
        items_html += f"""
        <div class="pt-metric-item">
            <div class="pt-metric-label">{m["label"]}</div>
            <div class="pt-metric-value">{m["value"]}</div>
            {delta_html}
        </div>
        """
    st.markdown(f'<div class="pt-metric-strip">{items_html}</div>', unsafe_allow_html=True)


def render_pill(text: str, variant: str = "muted") -> str:
    """Generate HTML for a semantic status or category pill."""
    variant_class = f"tf-pill-{variant}"
    return f'<span class="tf-pill {variant_class}">{text}</span>'
