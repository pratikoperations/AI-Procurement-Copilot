"""Regression contracts for hosted Steel routing and Android presentation readiness."""

from pathlib import Path

import pandas as pd
import pytest

from modules import hosted_readiness_ui, scenario


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

    import modules.steel_ux as steel_ux

    def fake_render(frame, assumptions):
        calls.append((frame.copy(), dict(assumptions)))
        raise SystemExit("governed route stopped")

    monkeypatch.setattr(steel_ux, "render_steel_governed_dashboard", fake_render)
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


def test_mobile_columns_are_forced_to_single_column() -> None:
    css = hosted_readiness_ui.HOSTED_READINESS_CSS
    mobile = css.split("@media (max-width: 900px)", 1)[1]
    assert "flex-direction: column !important" in mobile
    assert "flex: 1 1 100% !important" in mobile
    assert "width: 100% !important" in mobile
    assert ".stColumn" in mobile


def test_page_overflow_is_clipped_but_tables_scroll_internally() -> None:
    css = hosted_readiness_ui.HOSTED_READINESS_CSS
    assert "overflow-x: clip !important" in css
    assert '[data-testid="stDataFrame"]' in css
    assert "overflow-x: auto !important" in css
    assert "-webkit-overflow-scrolling: touch" in css


def test_select_focus_targets_actual_combobox_states() -> None:
    css = hosted_readiness_ui.HOSTED_READINESS_CSS
    assert '[role="combobox"]:focus-visible' in css
    assert '[role="combobox"][aria-expanded="true"]' in css
    assert "border-color: var(--aipc-select-focus) !important" in css
    assert '[role="combobox"][aria-invalid="true"]' in css
    assert "border-color: var(--aipc-error) !important" in css
    assert "outline: none" not in css


def test_landing_status_contract_has_one_erp_card() -> None:
    source = Path("app.py").read_text(encoding="utf-8")
    assert source.count('info("No live ERP integration")') == 1
