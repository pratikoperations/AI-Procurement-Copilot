from io import BytesIO
import json
from pathlib import Path

import pandas as pd

from modules.allocation import recommend_allocation
from modules.allocation_optimizer import optimize_allocation
from modules.dashboard import (
    C2_SYNTHETIC_DISCLOSURE,
    build_flexible_laminate_context,
    build_supplier_snapshot_display,
)
from modules.data_loader import get_demo_data, get_flexible_laminate_demo_suppliers
from modules.exports import (
    C2_EXPORT_DISCLAIMER,
    build_c2_export_manifest,
    build_decision_package_json,
    build_excel_workbook,
    build_readable_supplier_scores,
)
from modules.scenario import run_scenario_table
from modules.scoring import enrich_supplier_scores


def _assumptions(structure="PET / PE"):
    return {
        "category": "Packaging Procurement",
        "commodity": "Flexible Laminates",
        "laminate_structure": structure,
        "laminate_total_micron": 70,
        "annual_volume": 500000,
        "annual_volume_unit": "kg",
        "raw_material_shock": 0.0,
        "freight_shock": 0.0,
        "demand_change": 0.0,
        "fx_rate": 83.0,
        "display_currency": "USD",
        "category_profile": {"unit": "kg"},
    }


def _outputs():
    assumptions = _assumptions()
    data = get_flexible_laminate_demo_suppliers("PET / PE")
    scored = enrich_supplier_scores(data, assumptions)
    standard = recommend_allocation(scored, 500000, min_risk_score=0, min_esg_score=0)
    optimized = optimize_allocation(scored, 500000)["allocation_df"]
    scenarios = run_scenario_table(data, assumptions)
    return assumptions, data, scored, standard, optimized, scenarios


def test_c2_context_discloses_structure_unit_micron_and_claim_boundaries():
    context = build_flexible_laminate_context(_assumptions())
    assert context["Selected Laminate Structure"] == "PET / PE"
    assert context["Commercial Basis"] == "kg"
    assert context["Comparison Unit"] == "USD/kg"
    assert context["Total Micron"] == 70
    assert "Metadata only" in context["Micron Governance"]
    assert "not predictive accuracy" in context["Confidence Governance"]
    assert "not audited supplier evidence" in C2_SYNTHETIC_DISCLOSURE


def test_supplier_snapshot_contains_required_c2_decision_fields():
    assumptions, _, scored, _, _, _ = _outputs()
    display = build_supplier_snapshot_display(scored, assumptions)
    required = {
        "Technical Eligibility",
        "Technical Ineligibility Reasons",
        "Generic Failure Probability",
        "Laminate Failure Probability",
        "Generic Risk Penalty USD/kg",
        "Laminate Risk Penalty USD/kg",
        "Combined Risk Penalty USD/kg",
    }
    assert required.issubset(display.columns)


def test_scenario_table_separates_status_and_confidence_and_exposes_tooling_metadata():
    _, _, _, _, _, scenarios = _outputs()
    assert len(scenarios) == 7
    assert "Scenario Status / Reason" in scenarios.columns
    assert "Confidence Governance" in scenarios.columns
    assert "Scenario Assumption Version" in scenarios.columns
    assert "Tooling Replacement Applied" in scenarios.columns
    assert "Already New Tooling" in scenarios.columns
    assert "Tooling Not Applicable" in scenarios.columns
    tooling = scenarios.loc[scenarios["Scenario"] == "Tooling Replacement Scenario"].iloc[0]
    assert tooling["Tooling Replacement Applied"] == 0
    assert tooling["Already New Tooling"] == 3
    assert "No replacement applied" in tooling["Scenario Status / Reason"]


def test_non_applicable_and_no_winner_scenario_ux_are_explicit():
    _, _, _, _, _, scenarios = _outputs()
    metpet = scenarios.loc[scenarios["Scenario"] == "MetPET Availability Stress"].iloc[0]
    assert metpet["Scenario Applicable"] == False
    assert metpet["Winning Supplier"] == "Not applicable"
    assert metpet["Confidence"] == "Not applicable"
    capacity = scenarios.loc[scenarios["Scenario"] == "Press and Lamination Capacity Stress"].iloc[0]
    assert capacity["Winning Supplier"] == "No technically eligible supplier"
    assert capacity["Standard Allocation Status"] == "No allocation"
    assert capacity["Optimized Allocation Status"] == "No allocation"
    assert capacity["Confidence"] == 0.0
    assert capacity["Scenario Status / Reason"]


def test_supplier_export_preserves_visible_eligibility_tco_units_and_disclaimer():
    assumptions, _, scored, _, _, _ = _outputs()
    exported = build_readable_supplier_scores(
        scored,
        {"data_confidence_score": 100, "confidence_category": "Controlled"},
        {"status": "Human Review Required", "reason": "Synthetic demonstration"},
        display_currency="USD",
        fx_rate=83,
        annual_volume=500000,
        annual_volume_unit="kg",
    )
    visible = build_supplier_snapshot_display(scored, assumptions)
    assert exported["Supplier"].tolist() == visible["Supplier"].tolist()
    assert exported["Technical Eligibility"].tolist() == visible["Technical Eligibility"].tolist()
    assert set(exported["Commercial Basis"]) == {"kg"}
    assert set(exported["Comparison Unit"]) == {"USD/kg"}
    assert set(exported["Synthetic / Non-Certification Disclaimer"]) == {C2_EXPORT_DISCLAIMER}


def test_c2_export_manifest_matches_visible_winner_allocations_and_scenarios():
    _, _, scored, standard, optimized, scenarios = _outputs()
    manifest = build_c2_export_manifest(scored, standard, optimized, scenarios)
    eligible = scored[scored["technical_eligible"]]
    assert manifest["visible_winner"] == eligible.iloc[0]["Supplier"]
    assert manifest["commercial_basis"] == "kg"
    assert manifest["comparison_unit"] == "USD/kg"
    assert manifest["standard_allocation"] == standard.to_dict(orient="records")
    assert manifest["optimized_allocation"] == optimized.to_dict(orient="records")
    assert len(manifest["scenarios"]) == len(scenarios) == 7
    assert [row["Scenario"] for row in manifest["scenarios"]] == scenarios["Scenario"].tolist()
    assert [row["Winning Supplier"] for row in manifest["scenarios"]] == scenarios["Winning Supplier"].tolist()
    assert [row["Scenario Status / Reason"] for row in manifest["scenarios"]] == scenarios["Scenario Status / Reason"].tolist()
    assert manifest["scenario_assumption_versions"] == ["C2.5-SCENARIO-v1"]


def test_excel_contains_standard_optimized_scenario_and_governance_sheets():
    _, _, scored, standard, optimized, scenarios = _outputs()
    manifest = build_c2_export_manifest(scored, standard, optimized, scenarios)
    should_cost = pd.DataFrame([{"Component": "Controlled placeholder", "Unit Cost USD": 1.0}])
    workbook = build_excel_workbook(
        scored,
        should_cost,
        standard,
        scenarios,
        display_currency="USD",
        fx_rate=83,
        annual_volume=500000,
        annual_volume_unit="kg",
        optimized_allocation_df=optimized,
        c2_manifest=manifest,
    )
    sheets = pd.ExcelFile(BytesIO(workbook)).sheet_names
    assert {"Allocation", "Standard Allocation", "Optimized Allocation", "Scenarios", "C2 Governance"}.issubset(sheets)


def test_live_app_passes_same_c2_manifest_and_optimized_allocation_to_exports():
    source = Path("app.py").read_text(encoding="utf-8")
    assert "build_c2_export_manifest" in source
    assert "c2_manifest = (" in source
    assert 'optimized_allocation["allocation_df"]' in source
    assert 'optimized_allocation_df=optimized_allocation["allocation_df"]' in source
    assert source.count("c2_manifest=c2_manifest") == 2


def test_live_c2_excel_and_json_packages_share_governed_manifest():
    _, _, scored, standard, optimized, scenarios = _outputs()
    manifest = build_c2_export_manifest(scored, standard, optimized, scenarios)
    should_cost = pd.DataFrame([{"Component": "Controlled placeholder", "Unit Cost USD": 1.0}])
    workbook = build_excel_workbook(
        scored,
        should_cost,
        standard,
        scenarios,
        display_currency="USD",
        fx_rate=83,
        annual_volume=500000,
        annual_volume_unit="kg",
        optimized_allocation_df=optimized,
        c2_manifest=manifest,
    )
    optimized_sheet = pd.read_excel(BytesIO(workbook), sheet_name="Optimized Allocation")
    governance_sheet = pd.read_excel(BytesIO(workbook), sheet_name="C2 Governance")
    assert not optimized_sheet.empty
    assert set(governance_sheet["Field"]) >= {
        "selected_structure",
        "commercial_basis",
        "comparison_unit",
        "visible_winner",
        "eligible_supplier_count",
        "standard_allocation",
        "optimized_allocation",
        "scenarios",
        "scenario_assumption_versions",
        "disclaimer",
    }

    eligible = scored[scored["technical_eligible"]]
    payload = json.loads(
        build_decision_package_json(
            eligible.iloc[0],
            {"estimated_ebitda_opportunity_usd": 0.0},
            standard,
            scenarios,
            {"annual_saving_usd": 0.0},
            {"status": "Human Review Required"},
            c2_manifest=manifest,
        ).decode("utf-8")
    )
    exported_manifest = payload["flexible_laminates_governance"]
    assert exported_manifest == manifest
    assert exported_manifest["visible_winner"] == eligible.iloc[0]["Supplier"]
    assert exported_manifest["standard_allocation"] == standard.to_dict(orient="records")
    assert exported_manifest["optimized_allocation"] == optimized.to_dict(orient="records")
    assert [row["Scenario Status / Reason"] for row in exported_manifest["scenarios"]] == scenarios["Scenario Status / Reason"].tolist()
    assert exported_manifest["scenario_assumption_versions"] == ["C2.5-SCENARIO-v1"]


def test_non_c2_json_export_remains_without_c2_governance_block():
    payload = json.loads(
        build_decision_package_json(
            {"Supplier": "Supplier A"},
            {},
            pd.DataFrame(),
            pd.DataFrame(),
            {},
            {"status": "Human Review Required"},
        ).decode("utf-8")
    )
    assert "flexible_laminates_governance" not in payload


def test_existing_category_data_routes_remain_unchanged():
    corrugated = get_demo_data("Packaging Procurement", "Corrugated Board")
    kraft = get_demo_data("Raw Material Procurement", "Kraft Paper")
    pet = get_demo_data("Raw Material Procurement", "PET Resin")
    assert set(corrugated["Unit"]) == {"piece"}
    assert set(kraft["Material"]) == {"Kraft Paper"}
    assert set(pet["Material"]) == {"PET Resin"}
