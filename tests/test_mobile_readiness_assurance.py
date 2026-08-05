"""Static contracts for the governed mobile-readiness assurance layer."""

from pathlib import Path

from modules import hosted_readiness_ui


def test_six_governed_playwright_viewports_are_declared() -> None:
    source = Path("tests/browser/mobile-readiness.spec.ts").read_text(encoding="utf-8")
    for profile in (
        "small-android",
        "standard-android",
        "large-android",
        "foldable-inner",
        "tablet-portrait",
        "tablet-landscape",
    ):
        assert profile in source


def test_browser_acceptance_checks_page_overflow_and_sourcemate() -> None:
    source = Path("tests/browser/mobile-readiness.spec.ts").read_text(encoding="utf-8")
    assert "assertNoPageOverflow" in source
    assert "sourcemate_widget_panel" in source
    assert "toBeFocused" in source
    assert "toBeHidden" in source


def test_folded_phone_desktop_site_mode_is_governed() -> None:
    source = Path("tests/browser/mobile-readiness.spec.ts").read_text(encoding="utf-8")
    css = hosted_readiness_ui.HOSTED_READINESS_CSS
    assert "folded-phone-desktop-site-mode" in source
    assert "viewport: { width: 980, height: 1740 }" in source
    assert "screen: { width: 412, height: 915 }" in source
    assert "retains desktop-style multi-column layout" in source
    assert "gridTemplateColumns" in source
    assert "min-width: 900px" in css
    assert "max-width: 1000px" in css
    assert "width: min(18rem, 36vw)" in css
    assert "Preserve the desktop-style two-column presentation" in css


def test_collapsed_fold_sidebar_returns_width_to_main_content() -> None:
    source = Path("tests/browser/mobile-readiness.spec.ts").read_text(encoding="utf-8")
    css = hosted_readiness_ui.HOSTED_READINESS_CSS
    assert "returns collapsed sidebar width to the main content" in source
    assert "openEvidence.mainBox" in source
    assert "collapsedEvidence.mainBox" in source
    assert "captureFoldEvidence" in source
    assert ':has(button[aria-label="Open sidebar"])' in css
    assert "flex: 0 0 0 !important" in css
    assert "width: 0 !important" in css


def test_touch_targets_safe_areas_and_dynamic_viewport_are_governed() -> None:
    css = hosted_readiness_ui.HOSTED_READINESS_CSS
    assert "env(safe-area-inset-bottom, 0px)" in css
    assert "min-height: 100dvh" in css
    assert "min-height: 44px !important" in css
    assert "prefers-reduced-motion: reduce" in css


def test_mobile_acceptance_workflow_retains_failure_evidence() -> None:
    workflow = Path(".github/workflows/mobile-browser-acceptance.yml").read_text(encoding="utf-8")
    assert "npx playwright install --with-deps chromium" in workflow
    assert "Audit browser-test dependencies" in workflow
    assert "npm run audit:mobile" in workflow
    assert "Run focused Fold sidebar regression" in workflow
    assert "Run full mobile acceptance" in workflow
    assert "if: always()" in workflow
    assert "playwright-report" in workflow
    assert "test-results/mobile-acceptance" in workflow


def test_streamlit_runtime_uses_compatible_starlette() -> None:
    requirements = Path("requirements.txt").read_text(encoding="utf-8")
    assert "streamlit==1.59.1" in requirements
    assert "starlette==1.3.1" in requirements


def test_mobile_pack_preserves_scope_boundaries() -> None:
    document = Path("docs/MOBILE_READINESS_ACCEPTANCE.md").read_text(encoding="utf-8")
    assert "Business-logic changes: prohibited" in document
    assert "Native mobile application: excluded" in document
    assert "Framework migration: excluded" in document
    assert "Human procurement review: mandatory" in document
