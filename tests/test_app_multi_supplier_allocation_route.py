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
    assert "run_application_allocation" in imports["modules.multi_supplier_allocation_application"]
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
    assert "optimized_allocation_df=allocation_df" in source
    assert "allocation_df,\n        allocation_df,\n        scenario_df" in source


def test_route_states_and_human_approval_are_visible():
    source = APP_PATH.read_text(encoding="utf-8")
    assert "Governed Multi-Supplier Allocation Route" in source
    assert "Canonical allocation route is blocked" in source
    assert "Partial evidence captured before adapter failure" in source
    assert "No legacy allocation fallback is permitted" in source
    assert "not an autonomous award, approval record or ERP authorization" in source


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
