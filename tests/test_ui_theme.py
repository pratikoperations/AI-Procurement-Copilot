"""Deterministic presentation-contract tests for Build Group S1.1."""

from pathlib import Path

from modules import ui_theme


def test_status_palette_is_complete_and_stable() -> None:
    assert ui_theme.STATUS_COLORS == {
        "info": "#2F80ED",
        "success": "#2E8B57",
        "warning": "#B7791F",
        "error": "#C53030",
    }


def test_ui_css_covers_required_s1_1_surfaces() -> None:
    css = ui_theme.UI_CSS

    required_contracts = (
        '[data-testid="stMainBlockContainer"]',
        '[data-testid="stHorizontalBlock"]',
        '[data-testid="stMetric"]',
        '[data-testid="stAlert"]',
        '[data-testid="stSidebar"]',
        '.stButton > button',
        '.stDownloadButton > button',
        '@media (max-width: 768px)',
        '--aipc-info: #2F80ED',
        '--aipc-success: #2E8B57',
        '--aipc-warning: #B7791F',
        '--aipc-error: #C53030',
    )

    for contract in required_contracts:
        assert contract in css


def test_apply_ui_theme_injects_css_without_visible_code(monkeypatch) -> None:
    calls = []

    def fake_markdown(body: str, *, unsafe_allow_html: bool = False) -> None:
        calls.append((body, unsafe_allow_html))

    monkeypatch.setattr(ui_theme.st, "markdown", fake_markdown)

    ui_theme.apply_ui_theme()

    assert len(calls) == 1
    body, unsafe_allow_html = calls[0]
    assert body.startswith("<style>")
    assert body.endswith("</style>")
    assert unsafe_allow_html is True
    assert "st.json" not in body
    assert "st.code" not in body


def test_sidebar_applies_theme_before_rendering_controls() -> None:
    source = Path("modules/sidebar.py").read_text(encoding="utf-8")

    assert "from modules.ui_theme import apply_ui_theme" in source
    assert source.index("apply_ui_theme()") < source.index('st.sidebar.title("AI Procurement Copilot")')
