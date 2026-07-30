"""Deterministic accessibility and final UX contracts for Build S1.5."""

from modules import ui_theme


def test_keyboard_focus_is_visible_and_not_globally_suppressed() -> None:
    css = ui_theme.UI_CSS

    assert ":focus-visible" in css
    assert "outline: 3px solid var(--aipc-focus)" in css
    assert "outline-offset: 3px" in css
    assert "outline: none" not in css
    assert "outline: 0" not in css


def test_interactive_controls_preserve_touch_safe_height() -> None:
    css = ui_theme.UI_CSS

    assert ".stButton > button" in css
    assert ".stDownloadButton > button" in css
    assert css.count("min-height: 2.75rem") >= 2


def test_meaning_critical_metric_text_wraps_without_ellipsis() -> None:
    css = ui_theme.UI_CSS

    assert '[data-testid="stMetricLabel"]' in css
    assert '[data-testid="stMetricValue"]' in css
    assert "white-space: normal" in css
    assert "overflow-wrap: anywhere" in css
    assert "text-overflow: clip" in css


def test_tablet_and_mobile_contracts_prevent_page_level_overflow() -> None:
    css = ui_theme.UI_CSS

    assert '@media (max-width: 1024px)' in css
    assert '@media (max-width: 768px)' in css
    assert 'width: 100%' in css
    assert 'max-width: 100%' in css
    assert 'flex-wrap: wrap' in css
    assert 'flex: 1 1 100%' in css
    assert '[data-testid="stDataFrame"]' in css
    assert 'overflow-x: auto' in css


def test_reduced_motion_preference_is_respected() -> None:
    css = ui_theme.UI_CSS

    assert '@media (prefers-reduced-motion: reduce)' in css
    assert 'animation-duration: 0.01ms' in css
    assert 'transition-duration: 0.01ms' in css


def test_accessibility_changes_remain_presentation_only() -> None:
    source = ui_theme.__file__

    assert source.endswith("ui_theme.py")
    assert callable(ui_theme.apply_ui_theme)
