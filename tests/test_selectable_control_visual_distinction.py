"""Presentation-only contracts for selectable-control visual distinction."""
from pathlib import Path

from modules import selectable_control_ui


def test_selectbox_surface_is_scoped_and_semantically_distinct() -> None:
    css = selectable_control_ui.SELECTABLE_CONTROL_CSS

    assert '[data-testid="stSelectbox"]' in css
    assert 'rgba(47, 128, 237, 0.08)' in css
    assert 'rgba(47, 128, 237, 0.14)' in css
    assert '#58A6FF' in css
    assert '#C53030' in css
    assert '[data-testid="stExpander"]' not in css
    assert '[data-testid="stAlert"]' not in css
    assert '[data-testid="stMetric"]' not in css


def test_hover_focus_and_invalid_states_are_separate() -> None:
    css = selectable_control_ui.SELECTABLE_CONTROL_CSS

    assert ':hover > div' in css
    assert ':focus-within > div' in css
    assert ':has([aria-invalid="true"]) > div' in css

    focus_block = css.split(':focus-within > div {', 1)[1].split('}', 1)[0]
    invalid_block = css.split(':has([aria-invalid="true"]) > div {', 1)[1].split('}', 1)[0]
    assert '#58A6FF' in focus_block
    assert '#C53030' not in focus_block
    assert '#C53030' in invalid_block


def test_disabled_selectboxes_are_not_presented_as_active_selectable_controls() -> None:
    css = selectable_control_ui.SELECTABLE_CONTROL_CSS
    assert ':not(:has([aria-disabled="true"]))' in css


def test_global_entry_points_use_page_config_and_bootstrap_installs_surface() -> None:
    bootstrap = Path('sitecustomize.py').read_text(encoding='utf-8')
    app = Path('app.py').read_text(encoding='utf-8')
    explorer = Path('pages/8_Governed_Calculation_Explorer.py').read_text(encoding='utf-8')
    erp = Path('pages/9_ERP_Upload_Preview.py').read_text(encoding='utf-8')

    assert 'render_selectable_control_distinction' in bootstrap
    assert 'set_page_config_with_selectable_control_distinction' in bootstrap
    assert 'st.set_page_config' in app
    assert 'st.set_page_config' in explorer
    assert 'st.set_page_config' in erp


def test_sidebar_and_main_page_have_real_selectbox_surfaces() -> None:
    sidebar = Path('modules/sidebar.py').read_text(encoding='utf-8')
    explorer = Path('pages/8_Governed_Calculation_Explorer.py').read_text(encoding='utf-8')

    assert 'st.sidebar.selectbox(' in sidebar
    assert 'st.selectbox(' in explorer


def test_renderer_only_injects_css(monkeypatch) -> None:
    calls = []

    def fake_markdown(body: str, *, unsafe_allow_html: bool = False) -> None:
        calls.append((body, unsafe_allow_html))

    monkeypatch.setattr(selectable_control_ui.st, 'markdown', fake_markdown)
    selectable_control_ui.render_selectable_control_distinction()

    assert len(calls) == 1
    body, unsafe_allow_html = calls[0]
    assert body == selectable_control_ui.SELECTABLE_CONTROL_CSS
    assert unsafe_allow_html is True
