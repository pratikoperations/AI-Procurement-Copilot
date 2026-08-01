"""Deterministic presentation-contract tests for Build Group S1.1/S1.3."""

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


def test_s1_3_responsive_contracts_cover_validation_and_upload_surfaces() -> None:
    css = ui_theme.UI_CSS

    required_contracts = (
        '@media (max-width: 1024px)',
        '[data-testid="stHorizontalBlock"] > [data-testid="column"]',
        'flex-wrap: wrap',
        'flex: 1 1 100%',
        'width: 100% !important',
        '[data-testid="stMetricValue"] > div',
        'overflow-wrap: anywhere',
        'white-space: normal',
        '[data-testid="stExpanderDetails"]',
        'overflow-x: clip',
        '[data-testid="stDataFrame"]',
        '-webkit-overflow-scrolling: touch',
        '[data-testid="stFileUploader"]',
        '[data-testid="stFileUploaderFileName"]',
        'text-overflow: ellipsis',
    )

    for contract in required_contracts:
        assert contract in css


def test_metric_and_column_containers_can_shrink_without_horizontal_overflow() -> None:
    css = ui_theme.UI_CSS

    assert '[data-testid="stHorizontalBlock"] {' in css
    assert '[data-testid="stHorizontalBlock"] > [data-testid="column"] {' in css
    assert '[data-testid="stMetric"] {' in css
    assert css.count("min-width: 0") >= 6
    assert "max-width: 100%" in css


def test_select_focus_and_invalid_states_are_distinct() -> None:
    css = ui_theme.UI_CSS

    assert '--aipc-select-focus: #58A6FF' in css
    assert '[data-baseweb="select"]:focus-within > div' in css
    assert 'border-color: var(--aipc-select-focus) !important' in css
    assert '[data-baseweb="select"] [role="combobox"]:focus-visible' in css
    assert 'outline: 3px solid transparent !important' in css
    assert '[data-baseweb="select"]:has([aria-invalid="true"]) > div' in css
    assert 'border-color: var(--aipc-error) !important' in css


def test_normal_select_focus_does_not_use_error_or_yellow_marker() -> None:
    css = ui_theme.UI_CSS
    focus_block = css.split('[data-baseweb="select"]:focus-within > div {', 1)[1].split("}", 1)[0]
    combobox_block = css.split('[data-baseweb="select"] [role="combobox"]:focus-visible {', 1)[1].split("}", 1)[0]

    assert "var(--aipc-error)" not in focus_block
    assert "var(--aipc-focus)" not in focus_block
    assert "outline: 3px solid transparent !important" in combobox_block
    assert "outline: none" not in combobox_block
    assert "box-shadow: none !important" in combobox_block


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
