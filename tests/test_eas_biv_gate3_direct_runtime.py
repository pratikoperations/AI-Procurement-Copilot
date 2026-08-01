"""Direct authoritative runtime and production-export assurance for EAS-BIV Gate 3."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from io import BytesIO
import json
import math
from numbers import Integral, Real

import pandas as pd

from modules.allocation import recommend_allocation
from modules.allocation_optimizer import optimize_allocation
from modules.calculation_reconciliation_gate3 import reconcile_trace
from modules.calculation_trace_adapters import (
    build_recommendation_eligibility_trace,
    build_should_cost_trace,
    build_supplier_score_trace,
)
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
from modules.reconciliation_coverage import (
    ADAPTER_BACKED_COVERAGE_IDS,
    RECONCILIATION_COVERAGE,
    adapter_coverage_classification,
)
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

GENERIC = {"category":"Packaging Procurement","commodity":"Corrugated Board","annual_volume":500000,"raw_material_shock":0.0,"freight_shock":0.0,"demand_change":0.0,"fx_rate":83.0}
C2 = {"category":"Packaging Procurement","commodity":"Flexible Laminates","laminate_structure":"PET / PE","laminate_total_micron":70,"annual_volume":500000,"annual_volume_unit":"kg","raw_material_shock":0.0,"freight_shock":0.0,"demand_change":0.0,"fx_rate":83.0,"display_currency":"USD","category_profile":{"unit":"kg"}}
STEEL_COST = {"annual_volume_kg":500000,"base_steel_usd_per_kg":0.72,"profile_premium_usd_per_kg":0.05,"rolling_conversion_usd_per_kg":0.10,"zinc_cost_usd_per_kg":0.0,"paint_treatment_usd_per_kg":0.0,"energy_surcharge_usd_per_kg":0.04,"yield_pct":96.0,"slitting_cutting_usd_per_kg":0.025,"packing_usd_per_kg":0.015,"freight_usd_per_kg":0.045,"sourcing_route":"Domestic","import_duty_pct":0.0,"supplier_margin_pct":8.0}


def _snapshot_with_unavailable(value, path="$"):
    """Return a trace-safe copy plus exact unavailable non-finite paths."""
    unavailable = []
    if isinstance(value, pd.DataFrame):
        return _snapshot_with_unavailable(value.to_dict(orient="records"), path)
    if isinstance(value, pd.Series):
        return _snapshot_with_unavailable(value.to_dict(), path)
    if isinstance(value, tuple):
        value = list(value)
    if isinstance(value, list):
        normalized = []
        for index, item in enumerate(value):
            converted, paths = _snapshot_with_unavailable(item, f"{path}[{index}]")
            normalized.append(converted)
            unavailable.extend(paths)
        return normalized, tuple(unavailable)
    if isinstance(value, dict):
        normalized = {}
        for key, item in value.items():
            converted, paths = _snapshot_with_unavailable(item, f"{path}.{key}")
            normalized[str(key)] = converted
            unavailable.extend(paths)
        return normalized, tuple(unavailable)
    if value is pd.NA:
        return None, (path,)
    if isinstance(value, Real) and not isinstance(value, bool):
        if not math.isfinite(float(value)):
            return None, (path,)
        return (int(value) if isinstance(value, Integral) else float(value)), ()
    return value, ()


def _reconcile_adapter(trace, authoritative_output, service, unavailable=()):
    result = reconcile_trace(
        trace=trace,
        authoritative_service=service,
        authoritative_output=authoritative_output,
        calculation_id=trace.calculation_id,
        formula_id=trace.formula_id,
        formula_version=trace.formula_version,
        compared_fields=("",),
        unavailable_evidence=tuple(unavailable),
        repeated_trace_id=trace.trace_id,
    )
    expected_class = "unavailable_authoritative_intermediate" if unavailable else "exact_match"
    expected_status = "review_required" if unavailable else "clear"
    assert result.classification == expected_class
    assert result.blocking_status == expected_status
    assert result.human_review_status == "required"
    return result


def _should_cost_case(coverage_id, service, output, calculation_id, formula_id, category):
    normalized, unavailable = _snapshot_with_unavailable(output)
    trace = build_should_cost_trace(
        calculation_id=calculation_id,
        formula_id=formula_id,
        category=category,
        inputs={"fixture":"Gate 3 adapter-backed runtime", "coverage_id":coverage_id},
        authoritative_result=normalized,
    )
    assert trace.raw_output is not normalized
    result = _reconcile_adapter(trace, normalized, service, unavailable)
    assert adapter_coverage_classification(coverage_id) == "adapter_backed"
    return trace, normalized, result


def test_adapter_backed_should_cost_routes_reconcile_independently():
    cases = (
        ("REC-PET", "calculate_raw_material_should_cost:PET", calculate_raw_material_should_cost("PET Resin"), "PET-001", "F-RM-SHOULDCOST", "PET Resin"),
        ("REC-KRF", "calculate_raw_material_should_cost:Kraft", calculate_raw_material_should_cost("Kraft Paper"), "KRF-001", "F-RM-SHOULDCOST", "Kraft Paper"),
        ("REC-COR", "calculate_packaging_should_cost", calculate_packaging_should_cost(), "COR-001", "F-PKG-SHOULDCOST", "Corrugated Board"),
        ("REC-LAM", "calculate_flexible_laminate_should_cost", calculate_flexible_laminate_should_cost(), "LAM-004", "F-C2-SHOULDCOST", "Flexible Laminates"),
        ("REC-STL", "calculate_steel_should_cost", calculate_steel_should_cost("CR_COIL_COMMERCIAL", **STEEL_COST), "STL-003", "F-C3-SHOULDCOST", "Steel"),
    )
    for case in cases:
        _should_cost_case(*case)


def test_adapter_backed_scoring_and_eligibility_routes_reconcile():
    generic = get_demo_suppliers().copy()
    scored = enrich_supplier_scores(generic, GENERIC)
    score_output, score_unavailable = _snapshot_with_unavailable(scored.iloc[0].to_dict())
    score_trace = build_supplier_score_trace(
        inputs={**GENERIC, "fixture":"Gate 3 adapter-backed runtime"},
        authoritative_result=score_output,
        supplier=str(score_output.get("Supplier")),
    )
    assert score_trace.raw_output is not score_output
    _reconcile_adapter(score_trace, score_output, "enrich_supplier_scores", score_unavailable)

    eligibility = evaluate_recommendation_eligibility(
        {"is_valid":True,"errors":[],"warnings":[]},
        {"blocking_issues":[],"non_blocking_issues":[]},
        {"data_confidence_score":90,"confidence_category":"Strong"},
        scored,
        500000,
    )
    eligibility_output, eligibility_unavailable = _snapshot_with_unavailable(eligibility)
    eligibility_trace = build_recommendation_eligibility_trace(
        inputs={"category":"All", "fixture":"Gate 3 adapter-backed runtime"},
        authoritative_result=eligibility_output,
    )
    assert eligibility_trace.raw_output is not eligibility_output
    _reconcile_adapter(eligibility_trace, eligibility_output, "evaluate_recommendation_eligibility", eligibility_unavailable)


def test_broken_adapter_output_is_detected_and_blocked():
    _, normalized, trace_result = _should_cost_case(
        "REC-KRF", "calculate_raw_material_should_cost:Kraft",
        calculate_raw_material_should_cost("Kraft Paper"),
        "KRF-001", "F-RM-SHOULDCOST", "Kraft Paper",
    )
    assert trace_result.blocking_status == "clear"
    trace = build_should_cost_trace(
        calculation_id="KRF-001", formula_id="F-RM-SHOULDCOST", category="Kraft Paper",
        inputs={"fixture":"broken adapter adversarial"}, authoritative_result=normalized,
    )
    broken_output = deepcopy(trace.raw_output)
    key = next(iter(broken_output))
    broken_output[key] = "deliberately changed adapter field"
    broken_trace = replace(trace, raw_output=broken_output)
    result = reconcile_trace(
        trace=broken_trace,
        authoritative_service="calculate_raw_material_should_cost:Kraft",
        authoritative_output=normalized,
        calculation_id="KRF-001", formula_id="F-RM-SHOULDCOST", formula_version="1.0",
        compared_fields=("",),
    )
    assert result.blocking_status == "blocked"
    assert result.classification == "existing_business_logic_inconsistency"


def test_nonfinite_paths_are_disclosed_without_mutation():
    authoritative = {"finite_zero":0.0,"negative_zero":-0.0,"integer":7,"boolean":False,"nested":{"nan":float("nan"),"positive_inf":float("inf"),"negative_inf":float("-inf"),"missing":pd.NA}}
    original = deepcopy(authoritative)
    normalized, unavailable = _snapshot_with_unavailable(authoritative)
    assert unavailable == ("$.nested.nan", "$.nested.positive_inf", "$.nested.negative_inf", "$.nested.missing")
    assert normalized["finite_zero"] == 0.0
    assert math.copysign(1.0, normalized["negative_zero"]) == -1.0
    assert normalized["integer"] == 7 and normalized["boolean"] is False
    trace = build_should_cost_trace(
        calculation_id="TEST-NONFINITE", formula_id="F-RM-SHOULDCOST", category="Test",
        inputs={"fixture":"non-finite evidence"}, authoritative_result=normalized,
    )
    result = _reconcile_adapter(trace, normalized, "controlled_nonfinite_fixture", unavailable)
    assert result.unavailable_evidence == unavailable
    assert math.isnan(original["nested"]["nan"]) and math.isnan(authoritative["nested"]["nan"])
    assert authoritative["nested"]["positive_inf"] == original["nested"]["positive_inf"]


def test_non_adapter_routes_execute_but_are_explicitly_deferred():
    generic = get_demo_suppliers().copy(); generic_row = generic.iloc[0].to_dict()
    raw = get_demo_data("Raw Material Procurement", "PET Resin"); raw_row = raw.iloc[0].to_dict()
    c2 = get_flexible_laminate_demo_suppliers("PET / PE"); c2_row = c2.iloc[0].to_dict()
    steel = get_demo_data("Raw Material Procurement", "Steel")
    scored = enrich_supplier_scores(generic, GENERIC)
    steel_scored, steel_recommendation = score_and_recommend_steel_suppliers(steel, "CR_COIL_COMMERCIAL", 500000, 83.0)
    direct_outputs = {
        "REC-TCO-PKG": calculate_supplier_tco(generic_row, 500000),
        "REC-TCO-RM": calculate_raw_material_tco(raw_row, 500000),
        "REC-RISK-GEN": calculate_risk(generic_row),
        "REC-RISK-C2": assess_flexible_laminate_supplier(c2_row),
        "REC-RISK-C3": (steel_scored, steel_recommendation),
        "REC-SCORE-C3": (steel_scored, steel_recommendation),
        "REC-PER": calculate_performance_score(generic_row),
        "REC-ESG": calculate_esg_score(generic_row),
        "REC-TECH": scored[["Supplier","technical_eligible"]],
        "REC-ALLOC-STD": recommend_allocation(scored, 500000, min_risk_score=0, min_esg_score=0),
        "REC-ALLOC-OPT": optimize_allocation(scored, 500000),
        "REC-SCN-GEN": run_intelligence_scenario(generic, GENERIC, "Base Case"),
        "REC-SCN-C2": run_all_flexible_laminate_scenarios(c2, C2),
        "REC-SCN-C3": run_governed_steel_scenarios(steel, "CR_COIL_COMMERCIAL", 500000, 83.0, "Both"),
    }
    assert all(output is not None for output in direct_outputs.values())
    assert all(adapter_coverage_classification(key) == "unsupported_deferred_coverage" for key in direct_outputs)
    assert ADAPTER_BACKED_COVERAGE_IDS.isdisjoint(direct_outputs)
    registered = {item.coverage_id for item in RECONCILIATION_COVERAGE}
    assert set(direct_outputs) <= registered


def test_production_c2_excel_and_json_assurance():
    data = get_flexible_laminate_demo_suppliers("PET / PE"); scored = enrich_supplier_scores(data, C2)
    standard = recommend_allocation(scored, 500000, min_risk_score=0, min_esg_score=0)
    optimized = optimize_allocation(scored, 500000)["allocation_df"]
    scenarios = run_scenario_table(data, C2); manifest = build_c2_export_manifest(scored, standard, optimized, scenarios)
    workbook = build_excel_workbook(scored, pd.DataFrame([{"Component":"Controlled runtime evidence","Unit Cost USD":1.0}]), standard, scenarios, display_currency="USD", fx_rate=83.0, annual_volume=500000, annual_volume_unit="kg", optimized_allocation_df=optimized, c2_manifest=manifest)
    excel_result = assure_excel_evidence(workbook, "EXP-EV-005")
    assert excel_result.classification == "exact_match" and not excel_result.missing_locations
    winner = scored[scored["technical_eligible"].astype(bool)].iloc[0]
    payload = build_decision_package_json(winner,{"estimated_ebitda_opportunity_usd":0.0},standard,scenarios,{"annual_saving_usd":0.0},{"status":"Human Review Required"},c2_manifest=manifest)
    json_result = assure_json_evidence(payload, "EXP-EV-006")
    assert json_result.classification == "exact_match" and not json_result.missing_locations


def test_production_steel_excel_and_json_assurance():
    profile = "CR_COIL_COMMERCIAL"; suppliers = get_demo_data("Raw Material Procurement", "Steel")
    summary, details = run_governed_steel_scenarios(suppliers, profile, 500000, 83.0, "Both")
    state = normalize_steel_dependent_state({"steel_profile":profile,"steel_scenario":"Base Case","steel_sourcing_route":"Domestic","steel_zinc_cost_usd_per_kg":0.0,"steel_paint_treatment_usd_per_kg":0.0,"steel_import_duty_pct":0.0,"steel_substitution_status":"Non-applicable","display_currency":"Both"})
    selected = details["Base Case"]; manifest = build_steel_governance_manifest(state, summary, selected, 83.0, "Both")
    workbook = build_steel_excel_workbook(state, summary, selected, manifest)
    excel_result = assure_excel_evidence(workbook, "EXP-EV-003")
    assert excel_result.classification == "exact_match" and not excel_result.missing_locations
    payload = build_steel_json_export(manifest); json_result = assure_json_evidence(payload, "EXP-EV-007")
    assert json_result.classification == "exact_match" and not json_result.missing_locations
    assert "build_steel_decision_package_json" not in globals()
    assert pd.ExcelFile(BytesIO(workbook)).sheet_names == list(excel_result.present_locations)
    assert json.loads(payload.decode("utf-8"))["steel_governance"]["human_approval_required"] is True
