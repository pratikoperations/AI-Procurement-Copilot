"""Regression contracts for hosted Steel routing and Android presentation readiness."""

from pathlib import Path

import pandas as pd
import pytest

from modules import hosted_readiness_ui, scenario, steel_ux


def test_steel_route_is_detected_before_generic_scenarios() -> None:
    assert scenario._is_steel_route({
        "category": "Raw Material Procurement",
        "commodity": "Steel",
    })
    assert not scenario._is_steel_route({
        "category": "Raw Material Procurement",
        "commodity": "Kraft Paper",
    })
    assert not scenario._is_steel_route({
        "category": "Packaging Procurement",
        "commodity": "Flexible Laminates",
    })


def test_steel_route_dispatches_to_governed_dashboard(monkeypatch) -> None:
    calls = []
    monkeypatch.setattr(scenario, "apply_hosted_readiness_overrides", lambda: calls.append("css"))
    import modules.steel_ux as steel_ux_module

    def fake_render(frame, assumptions):
        calls.append((frame.copy(), dict(assumptions)))
        raise SystemExit("governed route stopped")

    monkeypatch.setattr(steel_ux_module, "render_steel_governed_dashboard", fake_render)
    frame = pd.DataFrame({"Supplier": ["A"]})
    assumptions = {"category": "Raw Material Procurement", "commodity": "Steel"}

    with pytest.raises(SystemExit, match="governed route stopped"):
        scenario.run_scenario_table(frame, assumptions)

    assert calls[0] == "css"
    assert calls[1][1] == assumptions


def test_generic_scenario_source_keeps_steel_guard_before_generic_loop() -> None:
    source = Path("modules/scenario.py").read_text(encoding="utf-8")
    guard = source.index("if _is_steel_route(assumptions):")
    generic = source.index("scenarios = [")
    assert guard < generic
    assert "render_steel_governed_dashboard(base_df, assumptions)" in source


def test_steel_widget_state_is_initialized_before_controls() -> None:
    source = Path("modules/steel_ux.py").read_text(encoding="utf-8")
    render_start = source.index("def render_steel_sidebar_controls")
    initialize = source.index("_initialize_steel_widget_state(assumptions)", render_start)
    profile_widget = source.index('key="steel_profile"', render_start)
    route_widget = source.index('key="steel_sourcing_route"', render_start)
    assert initialize < profile_widget < route_widget


def test_steel_render_path_has_no_post_widget_bound_key_assignment() -> None:
    source = Path("modules/steel_ux.py").read_text(encoding="utf-8")
    render = source[source.index("def render_steel_sidebar_controls"):source.index("def _display_allocation")]
    assert "apply_steel_state_transition(st.session_state" not in render
    assert 'st.session_state["steel_profile"] =' not in render
    assert 'st.session_state["steel_sourcing_route"] =' not in render
    assert "for key in STEEL_STATE_DEFAULTS" not in render


def test_steel_callback_updates_only_dependent_state(monkeypatch) -> None:
    state = {
        **steel_ux.STEEL_STATE_DEFAULTS,
        "steel_profile": "PPGI_COIL_Z120",
        "steel_sourcing_route": "Import",
    }
    monkeypatch.setattr(steel_ux.st, "session_state", state)
    steel_ux._sync_steel_dependents_from_widget_state()
    assert state["steel_profile"] == "PPGI_COIL_Z120"
    assert state["steel_sourcing_route"] == "Import"
    assert state["steel_zinc_cost_usd_per_kg"] == pytest.approx(0.08)
    assert state["steel_paint_treatment_usd_per_kg"] == pytest.approx(0.12)
    assert state["steel_import_duty_pct"] == pytest.approx(10.0)


def test_steel_profile_route_and_currency_transitions_remain_deterministic() -> None:
    state = dict(steel_ux.STEEL_STATE_DEFAULTS)
    for profile in steel_ux.STEEL_PROFILES:
        for route in ("Domestic", "Import", "Domestic"):
            normalized = steel_ux.apply_steel_state_transition(state, profile, route)
            assert normalized["steel_profile"] == profile
            assert normalized["steel_sourcing_route"] == route
            assert normalized["steel_import_duty_pct"] == (0.0 if route == "Domestic" else 10.0)
            for display in ("USD", "INR", "Both", "USD"):
                display_state = steel_ux.normalize_steel_dependent_state({**normalized, "display_currency": display})
                assert display_state["display_currency"] == display


def test_foldable_touch_layout_uses_readable_two_column_grid() -> None:
    css = hosted_readiness_ui.HOSTED_READINESS_CSS
    foldable = css.split("@media (hover: none) and (pointer: coarse) and (max-width: 1400px)", 1)[1]
    assert "grid-template-columns: repeat(2, minmax(0, 1fr)) !important" in foldable
    assert "width: 100% !important" in foldable
    assert ".stColumn" in foldable
    assert "overflow-x: clip !important" in foldable


def test_narrow_touch_layout_is_single_column() -> None:
    css = hosted_readiness_ui.HOSTED_READINESS_CSS
    narrow = css.split("/* Narrow touch screens use one column. */", 1)[1]
    assert "flex-direction: column !important" in narrow
    assert "flex: 1 1 100% !important" in narrow
    assert "width: 100% !important" in narrow


def test_page_overflow_is_clipped_but_tables_scroll_internally() -> None:
    css = hosted_readiness_ui.HOSTED_READINESS_CSS
    assert "overflow-x: clip !important" in css
    assert '[data-testid="stDataFrame"]' in css
    assert "overflow-x: auto !important" in css
    assert "-webkit-overflow-scrolling: touch" in css


def test_theme_level_interactive_accent_is_single_governed_blue() -> None:
    css = hosted_readiness_ui.HOSTED_READINESS_CSS
    root = css.split(":root {", 1)[1].split("}", 1)[0]
    assert "--aipc-focus: #58A6FF" in root
    assert "--aipc-select-focus: #58A6FF" in root
    assert "--primary-color: #58A6FF" in root
    assert "#F2C94C" not in root
    assert "#C53030" not in root


def test_obsolete_baseweb_select_selector_stack_is_removed() -> None:
    css = hosted_readiness_ui.HOSTED_READINESS_CSS
    assert '[data-baseweb="select"] > div' not in css
    assert '[data-baseweb="select"]:focus-within' not in css
    assert '> div > div:last-child' not in css
    assert "outline: none" not in css


def test_invalid_state_remains_red_by_semantics() -> None:
    css = hosted_readiness_ui.HOSTED_READINESS_CSS
    assert '[aria-invalid="true"]' in css
    assert "border-color: var(--aipc-error) !important" in css


def test_streamlit_theme_config_uses_governed_blue_primary() -> None:
    config = Path(".streamlit/config.toml").read_text(encoding="utf-8")
    assert 'base = "dark"' in config
    assert 'primaryColor = "#58A6FF"' in config
    assert 'backgroundColor = "#0E1117"' in config
    assert 'secondaryBackgroundColor = "#262730"' in config
    assert 'textColor = "#FAFAFA"' in config


def test_landing_status_contract_has_one_erp_card() -> None:
    source = Path("app.py").read_text(encoding="utf-8")
    assert source.count('info("No live ERP integration")') == 1
