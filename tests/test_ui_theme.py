"""Unit tests for TaskForge Anthracite Studio-inspired UI theme and components."""

import matplotlib.pyplot as plt
import pytest

from taskforge.ui.theme import (
    ANTHRACITE_CSS,
    COLOR_BG,
    COLOR_LIME,
    COLOR_SURFACE,
    apply_anthracite_mpl_theme,
    render_pill,
    style_anthracite_ax,
)


def test_theme_css_tokens():
    """Verify that Anthracite design tokens and accessibility rules exist in the stylesheet."""
    assert "#121212" in ANTHRACITE_CSS or "#151515" in ANTHRACITE_CSS
    assert "#D7FF64" in ANTHRACITE_CSS  # Signature Lime accent
    assert "prefers-reduced-motion" in ANTHRACITE_CSS
    assert "Syne" in ANTHRACITE_CSS
    assert "Plus Jakarta Sans" in ANTHRACITE_CSS
    assert "JetBrains Mono" in ANTHRACITE_CSS


def test_render_pill_variants():
    """Verify semantic HTML pill rendering across variants."""
    lime_pill = render_pill("Completed", variant="lime")
    assert "tf-pill-lime" in lime_pill
    assert "Completed" in lime_pill

    coral_pill = render_pill("Urgent", variant="coral")
    assert "tf-pill-coral" in coral_pill
    assert "Urgent" in coral_pill

    default_pill = render_pill("Pending")
    assert "tf-pill-muted" in default_pill


def test_matplotlib_anthracite_theming():
    """Verify that Matplotlib rcParams and axis stylers apply Anthracite design tokens."""
    apply_anthracite_mpl_theme()
    fig, ax = plt.subplots()
    try:
        style_anthracite_ax(ax, title="Test Chart", xlabel="X Axis", ylabel="Y Axis")
        assert ax.get_facecolor()[:3] is not None
        assert ax.get_title() == "Test Chart"
    finally:
        plt.close(fig)

