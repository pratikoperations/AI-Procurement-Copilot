"""Regression contracts for category-aware sidebar information architecture."""

from pathlib import Path

from modules import sidebar, steel_ux


APP_SOURCE = Path("app.py").read_text(encoding="utf-8")
SIDEBAR_SOURCE = Path("modules/sidebar.py").read_text(encoding="utf-8")
STEEL_SOURCE = Path("modules/steel_ux.py").read_text(encoding="utf-8")


def test_sidebar_has_focused_rendering_functions() -> None:
    for function_name in (
        "_render_sourcing_setup",
        "_render_kraft_inputs",
        "_render_laminate_inputs",
        "_render_commercial_basis",
        "_render_generic_scenario_inputs",
        "_render_generic_allocation_rules",
        "_render_about_roadmap",
    ):
        assert f"def {function_name}" in SIDEBAR_SOURCE


def test_sourcing_setup_remains_always_visible() -> None:
    section = SIDEBAR_SOURCE[
        SIDEBAR_SOURCE.index("def _render_sourcing_setup"):SIDEBAR_SOURCE.index("def _render_kraft_inputs")
    ]
    assert 'radio("Data Source"' in section
    assert 'selectbox("Category Engine"' in section
    assert 'selectbox("Commodity / Material"' in section
    assert "st.sidebar.expander" not in section


def test_category_inputs_are_category_specific() -> None:
    assert 'expander("Category Inputs — Kraft Paper", expanded=True)' in SIDEBAR_SOURCE
    assert 'expander("Category Inputs — Material Specification", expanded=True)' in SIDEBAR_SOURCE
    assert 'expander("Category Inputs — Printing", expanded=False)' in SIDEBAR_SOURCE
    assert 'expander("Category Inputs — Process Losses and Tooling", expanded=False)' in SIDEBAR_SOURCE
    assert 'expander("Category Inputs — Steel", expanded=True)' in STEEL_SOURCE


def test_commercial_scenario_allocation_and_roadmap_default_collapsed() -> None:
    assert 'expander("Commercial Basis", expanded=False)' in SIDEBAR_SOURCE
    assert 'expander("Scenario Inputs", expanded=False)' in SIDEBAR_SOURCE
    assert 'expander("Allocation Rules", expanded=False)' in SIDEBAR_SOURCE
    assert 'expander("About / Roadmap", expanded=False)' in SIDEBAR_SOURCE
    assert 'expander("Future Category Engines")' not in SIDEBAR_SOURCE


def test_steel_hides_nonoperative_generic_controls_but_keeps_contract_defaults() -> None:
    assert 'is_steel = category == "Raw Material Procurement" and commodity == "Steel"' in SIDEBAR_SOURCE
    assert "_render_generic_scenario_inputs(commodity, enabled=not is_steel)" in SIDEBAR_SOURCE
    assert "_render_generic_allocation_rules(enabled=not is_steel)" in SIDEBAR_SOURCE
    assert sidebar.GENERIC_SCENARIO_DEFAULTS == {
        "raw_material_shock": 0.0,
        "freight_shock": 0.0,
        "demand_change": 0.0,
        "procurement_intelligence_scenario": "Base Case",
    }
    assert sidebar.GENERIC_ALLOCATION_DEFAULTS == {
        "max_supplier_share": 75,
        "min_backup_share": 25,
        "min_risk_score": 55,
        "min_esg_score": 50,
    }


def test_procurement_intelligence_scenario_is_inside_generic_scenario_inputs() -> None:
    section = SIDEBAR_SOURCE[
        SIDEBAR_SOURCE.index("def _render_generic_scenario_inputs"):
        SIDEBAR_SOURCE.index("def _render_generic_allocation_rules")
    ]
    assert 'with st.sidebar.expander("Scenario Inputs", expanded=False):' in section
    assert '"Procurement Intelligence Scenario"' in section
    assert 'list(SCENARIOS.keys())' in section
    assert section.index('"Procurement Intelligence Scenario"') > section.index('expander("Scenario Inputs"')


def test_no_standalone_procurement_intelligence_scenario_remains_in_app() -> None:
    assert 'st.sidebar.selectbox("Procurement Intelligence Scenario"' not in APP_SOURCE
    assert 'selected_scenario = assumptions["procurement_intelligence_scenario"]' in APP_SOURCE
    assert "from modules.scenario_engine import SCENARIOS" not in APP_SOURCE


def test_scenario_selector_contract_is_present_for_generic_categories_and_defaulted_for_steel() -> None:
    scenario_section = SIDEBAR_SOURCE[
        SIDEBAR_SOURCE.index("def _render_generic_scenario_inputs"):
        SIDEBAR_SOURCE.index("def _render_generic_allocation_rules")
    ]
    assert 'if enabled:' in scenario_section
    assert '"procurement_intelligence_scenario": "Base Case"' in SIDEBAR_SOURCE
    assert 'procurement_intelligence_scenario=' not in APP_SOURCE


def test_steel_controls_render_once_before_dashboard() -> None:
    assert "render_steel_sidebar_controls({}) if is_steel else {}" in SIDEBAR_SOURCE
    dashboard = STEEL_SOURCE[STEEL_SOURCE.index("def render_steel_governed_dashboard"):]
    assert "render_steel_sidebar_controls(" not in dashboard
    assert "state = normalize_steel_dependent_state(assumptions)" in dashboard


def test_backward_compatible_sidebar_return_keys_are_retained() -> None:
    expected_keys = {
        "data_source", "category", "commodity", "category_profile", "fx_rate",
        "display_currency", "annual_volume", "annual_volume_unit",
        "raw_material_shock", "freight_shock", "demand_change",
        "procurement_intelligence_scenario",
        "max_supplier_share", "min_backup_share", "min_risk_score", "min_esg_score",
        "kraft_variant", "kraft_gsm", "kraft_strength_grade",
        "laminate_structure", "laminate_total_micron", "laminate_print_profile",
        "laminate_print_process", "laminate_number_of_colours", "laminate_adhesive_type",
        "laminate_printing_loss_pct", "laminate_lamination_loss_pct",
        "laminate_slitting_loss_pct", "laminate_tooling_status",
        "laminate_existing_tooling_available", "laminate_tooling_cost_per_colour_usd",
        "laminate_tooling_lifetime_volume_kg",
    }
    for key in expected_keys:
        assert f"{key}=" in SIDEBAR_SOURCE or f'"{key}"' in SIDEBAR_SOURCE


def test_existing_widget_keys_and_steel_state_keys_are_preserved() -> None:
    for key in (
        sidebar.LAMINATE_PRINT_PROFILE_KEY,
        sidebar.LAMINATE_COLOUR_COUNT_KEY,
        sidebar.LAMINATE_TOOLING_STATUS_KEY,
        sidebar.LAMINATE_TOOLING_AVAILABILITY_KEY,
        sidebar.LAMINATE_TOOLING_COST_KEY,
        sidebar.LAMINATE_TOOLING_LIFETIME_KEY,
    ):
        assert key in SIDEBAR_SOURCE
    for key in steel_ux.STEEL_STATE_DEFAULTS:
        assert key in STEEL_SOURCE


def test_no_business_or_export_modules_are_modified_by_sidebar_contract() -> None:
    forbidden_imports = (
        "modules.allocation",
        "modules.scoring",
        "modules.steel_exports",
        "modules.exports",
    )
    sidebar_import_block = SIDEBAR_SOURCE.split("FX_RATE_MIN", 1)[0]
    for forbidden in forbidden_imports:
        assert forbidden not in sidebar_import_block
