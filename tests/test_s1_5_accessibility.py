"""Deterministic accessibility and responsive UX contracts for Build S1.5/S1.5.1."""

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


def test_meaning_critical_metric_text_overrides_generated_ellipsis() -> None:
    css = ui_theme.UI_CSS

    assert '[data-testid="stMetricLabel"] *' in css
    assert '[data-testid="stMetricValue"] *' in css
    assert '[data-testid="stMetricDelta"] *' in css
    assert "white-space: normal !important" in css
    assert "overflow: visible !important" in css
    assert "text-overflow: clip !important" in css
    assert "overflow-wrap: anywhere !important" in css
    assert "word-break: break-word !important" in css


def test_viewport_wrappers_are_width_bounded_and_clipped() -> None:
    css = ui_theme.UI_CSS

    assert 'html,' in css
    assert '[data-testid="stAppViewContainer"]' in css
    assert '[data-testid="stMain"]' in css
    assert '[data-testid="stMainBlockContainer"]' in css
    assert "max-width: 100%" in css
    assert "min-width: 0" in css
    assert "overflow-x: clip" in css
    assert "box-sizing: border-box" in css


def test_tablet_columns_wrap_with_explicit_override() -> None:
    css = ui_theme.UI_CSS

    assert '@media (max-width: 1024px)' in css
    assert "flex-wrap: wrap !important" in css
    assert "flex: 1 1 calc(50% - var(--aipc-space-4)) !important" in css
    assert "width: calc(50% - var(--aipc-space-4)) !important" in css
    assert "min-width: min(15rem, 100%) !important" in css


def test_mobile_columns_stack_without_intrinsic_minimum_width() -> None:
    css = ui_theme.UI_CSS

    assert '@media (max-width: 768px)' in css
    assert "flex: 1 1 100% !important" in css
    assert "width: 100% !important" in css
    assert "max-width: 100% !important" in css
    assert "min-width: 0 !important" in css


def test_sidebar_is_bounded_to_the_available_viewport() -> None:
    css = ui_theme.UI_CSS

    assert '[data-testid="stSidebar"]' in css
    assert "max-width: min(21rem, 88vw)" in css
    assert '[data-testid="stSidebarContent"]' in css


def test_wide_tables_keep_internal_horizontal_scrolling() -> None:
    css = ui_theme.UI_CSS

    assert '[data-testid="stDataFrame"]' in css
    assert '[data-testid="stTable"]' in css
    assert "overflow-x: auto" in css
    assert "-webkit-overflow-scrolling: touch" in css


def test_reduced_motion_preference_is_respected() -> None:
    css = ui_theme.UI_CSS

    assert '@media (prefers-reduced-motion: reduce)' in css
    assert 'animation-duration: 0.01ms' in css
    assert 'transition-duration: 0.01ms' in css


def test_responsive_correction_remains_presentation_only() -> None:
    source = ui_theme.__file__

    assert source.endswith("ui_theme.py")
    assert callable(ui_theme.apply_ui_theme)
