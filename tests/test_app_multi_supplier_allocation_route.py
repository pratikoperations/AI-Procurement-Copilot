from __future__ import annotations

import ast
from pathlib import Path


APP_PATH = Path("app.py")
PROCUREMENT_UI_PATH = Path("modules/procurement_intelligence_ui.py")


def _app_tree():
    return ast.parse(APP_PATH.read_text(encoding="utf-8"))


def test_app_imports_canonical_application_integration_only():
    tree = _app_tree()
    imports = {
        node.module: {alias.name for alias in node.names}
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }
    canonical_imports = imports["modules.multi_supplier_allocation_application"]
    assert "run_application_allocation" in canonical_imports
    assert "build_route_decision_control" in canonical_imports
    assert "modules.allocation" not in imports
    assert "modules.allocation_optimizer" not in imports


def test_app_never_calls_legacy_allocation_functions():
    tree = _app_tree()
    called_names = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert "recommend_allocation" not in called_names
    assert "optimize_allocation" not in called_names


def test_governed_and_standard_paths_use_canonical_application_route():
    source = APP_PATH.read_text(encoding="utf-8")
    assert source.count("run_application_allocation(") == 2
    assert 'return run_application_allocation(outputs["SCORING_TCO"], assumptions)' in source
    assert "application_allocation = run_application_allocation(scored_df, assumptions)" in source


def test_allocation_consumers_receive_one_projected_result():
    source = APP_PATH.read_text(encoding="utf-8")
    assert "assess_procurement_risks(scored_df, allocation_df)" in source
    assert "generate_decision(scored_df, allocation_df, risk_result)" in source
    assert "suppliers_df, scored_df, allocation_df," in source
    assert "scored_df, allocation_df, value_metrics" in source

    canonical_manifest_call = (
        "build_c2_export_manifest(\n"
        "        scored_df,\n"
        "        allocation_df,\n"
        "        scenario_df,\n"
        "    )"
    )
    assert canonical_manifest_call in source
    assert "allocation_df,\n        allocation_df,\n        scenario_df" not in source
    assert "optimized_allocation_df=allocation_df" not in source
    assert "standard_allocation=" not in source
    assert "optimized_allocation_df=" not in source


def test_route_states_and_human_approval_are_visible():
    source = APP_PATH.read_text(encoding="utf-8")
    assert "Governed Multi-Supplier Allocation Route" in source
    assert "Canonical allocation route is blocked" in source
    assert "Partial evidence captured before adapter failure" in source
    assert "No legacy allocation fallback is permitted" in source
    assert "No autonomous award, approval record or ERP authorization is created" in source


def test_blocked_route_suppresses_final_award_and_executive_dashboard():
    source = APP_PATH.read_text(encoding="utf-8")
    assert 'route_decision_control = build_route_decision_control(allocation_route_result, eligibility)' in source
    assert 'final_award_language_allowed = route_decision_control["final_award_language_allowed"]' in source
    assert "if final_award_language_allowed:" in source
    assert "Final award and allocation recommendation withheld" in source
    assert "if recommendation_language_allowed:\n    render_executive_dashboard" in source


def test_blocked_route_governs_executive_outputs_and_downloads():
    source = APP_PATH.read_text(encoding="utf-8")
    assert "ANALYTICAL-ONLY OUTPUT" in source
    assert "No supplier has been selected for award" in source
    assert "Supplier clarification request — no award decision" in source
    assert "Recommendation-bearing Excel, memo, allocation and decision-audit downloads are withheld" in source
    assert "Download Clarification Email" in source


def test_procurement_intelligence_receives_combined_recommendation_control():
    source = APP_PATH.read_text(encoding="utf-8")
    assert "recommendation_allowed=recommendation_language_allowed" in source
    ui_source = PROCUREMENT_UI_PATH.read_text(encoding="utf-8")
    assert "route_allows_recommendation" in ui_source
    assert "Supplier award and allocation recommendation language is withheld" in ui_source
    assert "No supplier has been selected for award" in ui_source


def test_procurement_intelligence_hides_legacy_scenario_allocation():
    source = PROCUREMENT_UI_PATH.read_text(encoding="utf-8")
    assert "Governed Multi-Supplier Allocation" in source
    assert "No legacy scenario allocation is displayed" in source
    assert 'scenario_result["allocation"]' not in source
    assert "Recommended supplier under scenario" not in source


def test_display_currency_is_not_passed_to_canonical_route_call():
    source = APP_PATH.read_text(encoding="utf-8")
    assert "run_application_allocation(scored_df, assumptions)" in source
    assert "comparison_currency=display_currency" not in source
