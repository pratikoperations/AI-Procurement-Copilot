"""Direct authoritative runtime and production-export assurance for EAS-BIV Gate 3."""
from __future__ import annotations

from io import BytesIO
import json

import pandas as pd

from modules.allocation import recommend_allocation
from modules.allocation_optimizer import optimize_allocation
from modules.calculation_reconciliation_gate3 import reconcile_trace
from modules.calculation_trace import build_trace
from modules.data_loader import get_demo_data, get_demo_suppliers, get_flexible_laminate_demo_suppliers
from modules.esg import calculate_esg_score
from modules.evidence_assurance import assure_excel_evidence, assure_json_evidence
from modules.exports import build_c2_export_manifest, build_decision_package_json, build_excel_workbook
from modules.flexible_laminate_cost import calculate_flexible_laminate_should_cost
from modules.flexible_laminate_risk import assess_flexible_laminate_supplier
from modules.performance import calculate_performance_score
from modules.raw_material_cost import calculate_raw_material_should_cost
from modules.raw_material_risk import calculate_raw_material_risk
from modules.raw_material_tco import calculate_raw_material_tco
from modules.recommendation_eligibility import evaluate_recommendation_eligibility
from modules.risk import calculate_risk
from modules.scenario import run_scenario_table
from modules.scenario_engine import run_all_flexible_laminate_scenarios, run_intelligence_scenario
from modules.scoring import enrich_supplier_scores
from modules.should_cost import calculate_packaging_should_cost
from modules.steel_cost import calculate_steel_should_cost
from modules.steel_exports import build_steel_excel_workbook, build_steel_governance_manifest, build_steel_json_export
from modules.steel_risk import score_and_recommend_steel_suppliers
from modules.steel_scenario import run_governed_steel_scenarios
from modules.steel_ux import normalize_steel_dependent_state
from modules.tco import calculate_supplier_tco


GENERIC_ASSUMPTIONS = {
    "category": "Packaging Procurement",
    "commodity": "Corrugated Board",
    "annual_volume": 500_000,
    "raw_material_shock": 0.0,
    "freight_shock": 0.0,
    "demand_change": 0.0,
    "fx_rate": 83.0,
}
C2_ASSUMPTIONS = {
    "category": "Packaging Procurement",
    "commodity": "Flexible Laminates",
    "laminate_structure": "PET / PE",
    "laminate_total_micron": 70,
    "annual_volume": 500_000,
    "annual_volume_unit": "kg",
    "raw_material_shock": 0.0,
    "freight_shock": 0.0,
    "demand_change": 0.0,
    "fx_rate": 83.0,
    "display_currency": "USD",
    "category_profile": {"unit": "kg"},
}
STEEL_COST_INPUTS = {
    "annual_volume_kg": 500_000,
    "base_steel_usd_per_kg": 0.72,
    "profile_premium_usd_per_kg": 0.05,
    "rolling_conversion_usd_per_kg": 0.10,
    "zinc_cost_usd_per_kg": 0.0,
    "paint_treatment_usd_per_kg": 0.0,
    "energy_surcharge_usd_per_kg": 0.04,
    "yield_pct": 96.0,
    "slitting_cutting_usd_per_kg": 0.025,
    "packing_usd_per_kg": 0.015,
    "freight_usd_per_kg": 0.045,
    "sourcing_route": "Domestic",
    "import_duty_pct": 0.0,
    "supplier_margin_pct": 8.0,
}


def _snapshot(value):
    if isinstance(value, pd.DataFrame):
        return value.to_dict(orient="records")
    if isinstance(value, pd.Series):
        return value.to_dict()
    if isinstance(value, tuple):
        return [_snapshot(item) for item in value]
    if isinstance(value, list):
        return [_snapshot(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _snapshot(item) for key, item in value.items()}
    return value


def _assert_direct_reconciliation(service, output, calculation_id, formula_id, category):
    snapshot = _snapshot(output)
    trace = build_trace(
        calculation_id=calculation_id,
        formula_id=formula_id,
        formula_version="1.0",
        category=category,
        input_snapshot={"fixture": "Gate 3 direct authoritative runtime"},
        raw_output=snapshot,
        configuration_versions={},
    )
    result = reconcile_trace(
        trace=trace,
        authoritative_service=service,
        authoritative_output=snapshot,
        calculation_id=calculation_id,
        formula_id=formula_id,
        formula_version="1.0",
        compared_fields=("",),
        repeated_trace_id=trace.trace_id,
    )
    assert result.classification == "exact_match"
    assert result.blocking_status == "clear"
    assert result.human_review_status == "required"


def test_direct_should_cost_tco_risk_scoring_and_eligibility_routes_reconcile():
    generic = get_demo_suppliers().copy()
    generic_row = generic.iloc[0].to_dict()
    raw = get_demo_data("Raw Material Procurement", "PET Resin").copy()
    raw_row = raw.iloc[0].to_dict()
    c2 = get_flexible_laminate_demo_suppliers("PET / PE").copy()
    c2_row = c2.iloc[0].to_dict()
    steel = get_demo_data("Raw Material Procurement", "Steel").copy()

    outputs = (
        ("calculate_raw_material_should_cost:PET", calculate_raw_material_should_cost("PET Resin"), "PET-001", "F-RM-SHOULDCOST", "PET Resin"),
        ("calculate_raw_material_should_cost:Kraft", calculate_raw_material_should_cost("Kraft Paper"), "KRF-001", "F-RM-SHOULDCOST", "Kraft Paper"),
        ("calculate_packaging_should_cost", calculate_packaging_should_cost(), "COR-001", "F-PKG-SHOULDCOST", "Corrugated Board"),
        ("calculate_flexible_laminate_should_cost", calculate_flexible_laminate_should_cost(), "LAM-004", "F-C2-SHOULDCOST", "Flexible Laminates"),
        ("calculate_steel_should_cost", calculate_steel_should_cost("CR_COIL_COMMERCIAL", **STEEL_COST_INPUTS), "STL-003", "F-C3-SHOULDCOST", "Steel"),
        ("calculate_supplier_tco", calculate_supplier_tco(generic_row, 500_000), "TCO-001", "F-TCO-PKG", "Packaging"),
        ("calculate_raw_material_tco", calculate_raw_material_tco(raw_row, 500_000), "TCO-002", "F-TCO-RM", "Raw materials"),
        ("calculate_risk", calculate_risk(generic_row), "RSK-001", "F-RISK-GEN", "Generic"),
        ("assess_flexible_laminate_supplier", assess_flexible_laminate_supplier(c2_row), "RSK-002", "F-RISK-GEN", "Flexible Laminates"),
        ("calculate_raw_material_risk", calculate_raw_material_risk(raw_row), "RSK-RM", "F-RISK-GEN", "Raw materials"),
        ("calculate_performance_score", {"performance_score": calculate_performance_score(generic_row)}, "PER-001", "F-PERFORMANCE", "Packaging and Raw materials"),
        ("calculate_esg_score", {"esg_score": calculate_esg_score(generic_row)}, "ESG-001", "F-ESG", "Packaging and Raw materials"),
    )
    for service, output, calculation_id, formula_id, category in outputs:
        _assert_direct_reconciliation(service, output, calculation_id, formula_id, category)

    scored = enrich_supplier_scores(generic, GENERIC_ASSUMPTIONS)
    _assert_direct_reconciliation("enrich_supplier_scores:scoring", scored, "SCR-001", "F-SCORE-GEN", "Packaging and Raw materials")
    _assert_direct_reconciliation(
        "enrich_supplier_scores:technical_eligibility",
        scored[["Supplier", "technical_eligible"]],
        "ELG-TECH", "F-ELIGIBILITY", "Cross-category",
    )

    steel_scored, steel_recommendation = score_and_recommend_steel_suppliers(
        steel, "CR_COIL_COMMERCIAL", 500_000, 83.0
    )
    _assert_direct_reconciliation(
        "score_and_recommend_steel_suppliers",
        {"scored": steel_scored, "recommendation": steel_recommendation},
        "SCR-002", "F-SCORE-STEEL", "Steel",
    )

    eligibility = evaluate_recommendation_eligibility(
        {"is_valid": True, "errors": [], "warnings": []},
        {"blocking_issues": [], "non_blocking_issues": []},
        {"data_confidence_score": 90, "confidence_category": "Strong"},
        scored,
        500_000,
    )
    _assert_direct_reconciliation(
        "evaluate_recommendation_eligibility", eligibility,
        "ELG-001", "F-ELIGIBILITY", "All",
    )


def test_direct_allocation_and_scenario_routes_reconcile():
    generic = get_demo_suppliers().copy()
    scored = enrich_supplier_scores(generic, GENERIC_ASSUMPTIONS)
    standard = recommend_allocation(scored, 500_000, min_risk_score=0, min_esg_score=0)
    optimized = optimize_allocation(scored, 500_000)
    generic_scenario = run_intelligence_scenario(generic, GENERIC_ASSUMPTIONS, "Base Case")

    c2 = get_flexible_laminate_demo_suppliers("PET / PE").copy()
    c2_scenarios = run_all_flexible_laminate_scenarios(c2, C2_ASSUMPTIONS)

    steel = get_demo_data("Raw Material Procurement", "Steel").copy()
    steel_summary, steel_details = run_governed_steel_scenarios(
        steel, "CR_COIL_COMMERCIAL", 500_000, 83.0, "Both"
    )

    routes = (
        ("recommend_allocation", standard, "ALC-001", "F-ALLOC-STD", "Generic"),
        ("optimize_allocation", optimized, "ALC-002", "F-ALLOC-OPT", "Generic"),
        ("run_intelligence_scenario", generic_scenario, "SCN-001", "F-SCENARIO-GENERIC", "Generic"),
        ("run_all_flexible_laminate_scenarios", c2_scenarios, "SCN-002", "F-SCENARIO-C2", "Flexible Laminates"),
        ("run_governed_steel_scenarios", {"summary": steel_summary, "details": steel_details}, "SCN-003", "F-SCENARIO-STEEL", "Steel"),
    )
    for service, output, calculation_id, formula_id, category in routes:
        _assert_direct_reconciliation(service, output, calculation_id, formula_id, category)


def test_production_c2_excel_and_json_outputs_pass_registered_assurance():
    data = get_flexible_laminate_demo_suppliers("PET / PE")
    scored = enrich_supplier_scores(data, C2_ASSUMPTIONS)
    standard = recommend_allocation(scored, 500_000, min_risk_score=0, min_esg_score=0)
    optimized = optimize_allocation(scored, 500_000)["allocation_df"]
    scenarios = run_scenario_table(data, C2_ASSUMPTIONS)
    manifest = build_c2_export_manifest(scored, standard, optimized, scenarios)
    should_cost = pd.DataFrame([{"Component": "Controlled runtime evidence", "Unit Cost USD": 1.0}])

    workbook = build_excel_workbook(
        scored, should_cost, standard, scenarios,
        display_currency="USD", fx_rate=83.0,
        annual_volume=500_000, annual_volume_unit="kg",
        optimized_allocation_df=optimized, c2_manifest=manifest,
    )
    excel_result = assure_excel_evidence(workbook, "EXP-EV-005")
    assert excel_result.classification == "exact_match"
    assert excel_result.missing_locations == ()

    winner = scored[scored["technical_eligible"].astype(bool)].iloc[0]
    payload = build_decision_package_json(
        winner,
        {"estimated_ebitda_opportunity_usd": 0.0},
        standard,
        scenarios,
        {"annual_saving_usd": 0.0},
        {"status": "Human Review Required"},
        c2_manifest=manifest,
    )
    json_result = assure_json_evidence(payload, "EXP-EV-006")
    assert json_result.classification == "exact_match"
    assert json_result.missing_locations == ()


def test_production_steel_excel_and_json_outputs_pass_registered_assurance():
    profile = "CR_COIL_COMMERCIAL"
    suppliers = get_demo_data("Raw Material Procurement", "Steel")
    summary, details = run_governed_steel_scenarios(suppliers, profile, 500_000, 83.0, "Both")
    state = normalize_steel_dependent_state({
        "steel_profile": profile,
        "steel_scenario": "Base Case",
        "steel_sourcing_route": "Domestic",
        "steel_zinc_cost_usd_per_kg": 0.0,
        "steel_paint_treatment_usd_per_kg": 0.0,
        "steel_import_duty_pct": 0.0,
        "steel_substitution_status": "Non-applicable",
        "display_currency": "Both",
    })
    selected = details["Base Case"]
    manifest = build_steel_governance_manifest(state, summary, selected, 83.0, "Both")

    workbook = build_steel_excel_workbook(state, summary, selected, manifest)
    excel_result = assure_excel_evidence(workbook, "EXP-EV-003")
    assert excel_result.classification == "exact_match"
    assert excel_result.missing_locations == ()

    payload = build_steel_json_export(manifest)
    json_result = assure_json_evidence(payload, "EXP-EV-007")
    assert json_result.classification == "exact_match"
    assert json_result.missing_locations == ()
    assert "build_steel_decision_package_json" not in globals()

    # Confirm the generated workbook is readable without changing its schema.
    assert pd.ExcelFile(BytesIO(workbook)).sheet_names == list(excel_result.present_locations)
    assert json.loads(payload.decode("utf-8"))["steel_governance"]["human_approval_required"] is True
