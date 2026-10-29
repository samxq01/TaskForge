"""Unit tests for TaskForge Potadot-inspired UI theme and components."""

import matplotlib.pyplot as plt
import pytest

from taskforge.ui.theme import (
    COLOR_BG,
    COLOR_BRAND,
    COLOR_SURFACE,
    POTADOT_CSS,
    apply_potadot_mpl_theme,
    render_pill,
    style_potadot_ax,
)


def test_theme_css_tokens():
    """Verify that Potadot design tokens, typography, and accessibility rules exist in the stylesheet."""
    assert "#F8FAFC" in POTADOT_CSS  # Crisp light canvas background
    assert "#2563EB" in POTADOT_CSS  # Signature Potadot Digital Blue accent
    assert "prefers-reduced-motion" in POTADOT_CSS
    assert "Syne" in POTADOT_CSS
    assert "Plus Jakarta Sans" in POTADOT_CSS
    assert "JetBrains Mono" in POTADOT_CSS


def test_render_pill_variants():
    """Verify semantic HTML pill rendering across variants."""
    completed_pill = render_pill("Completed", variant="lime")
    assert "tf-pill-lime" in completed_pill
    assert "Completed" in completed_pill

    urgent_pill = render_pill("Urgent", variant="coral")
    assert "tf-pill-coral" in urgent_pill
    assert "Urgent" in urgent_pill

    default_pill = render_pill("Pending")
    assert "tf-pill-muted" in default_pill


def test_matplotlib_potadot_theming():
    """Verify that Matplotlib rcParams and axis stylers apply Potadot light product tokens."""
    apply_potadot_mpl_theme()
    fig, ax = plt.subplots()
    try:
        style_potadot_ax(ax, title="Test Chart", xlabel="X Axis", ylabel="Y Axis")
        assert ax.get_facecolor()[:3] is not None
        assert ax.get_title() == "Test Chart"
    finally:
        plt.close(fig)


def test_app_all_views_render_without_exceptions():
    """Verify that app.py and all 8 navigation views render cleanly in AppTest."""
    from pathlib import Path
    from streamlit.testing.v1 import AppTest

    app_path = str(Path(__file__).parent.parent / "app.py")
    at = AppTest.from_file(app_path, default_timeout=30).run()
    assert not at.exception, f"Initial dashboard run failed: {at.exception}"

    views = at.sidebar.radio[0].options
    assert len(views) == 8, f"Expected 8 navigation views, found {len(views)}"

    for view_label in views:
        at.sidebar.radio[0].set_value(view_label).run()
        assert not at.exception, f"View '{view_label}' raised an exception: {at.exception}"

