from io import BytesIO
import json
from pathlib import Path

import pandas as pd

from modules.dashboard import (
    C2_SYNTHETIC_DISCLOSURE,
    build_flexible_laminate_context,
    build_supplier_snapshot_display,
)
from modules.data_loader import get_demo_data, get_flexible_laminate_demo_suppliers
from modules.exports import (
    C2_EXPORT_CONTRACT_VERSION,
    C2_EXPORT_DISCLAIMER,
    build_c2_export_manifest,
    build_decision_package_json,
    build_excel_workbook,
    build_readable_supplier_scores,
)
from modules.multi_supplier_allocation_application import run_application_allocation
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
        "data_source": "Synthetic Demo",
        "required_awardee_count": 2,
        "minimum_awarded_share_pct": 10.0,
        "max_supplier_share": 75.0,
        "min_backup_share": 25.0,
        "min_risk_score": 0.0,
        "min_esg_score": 0.0,
        "capacity_utilization_ceiling_pct": 90.0,
        "category_profile": {"unit": "kg"},
    }


def _outputs():
    assumptions = _assumptions()
    data = get_flexible_laminate_demo_suppliers("PET / PE")
    scored = enrich_supplier_scores(data, assumptions)
    canonical = run_application_allocation(scored, assumptions).allocation_df
    scenarios = run_scenario_table(data, assumptions)
    return assumptions, data, scored, canonical, scenarios


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
    assumptions, _, scored, _, _ = _outputs()
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


def test_scenario_table_exposes_canonical_status_and_tooling_metadata():
    _, _, _, _, scenarios = _outputs()
    assert len(scenarios) == 7
    required = {
        "Scenario Status / Reason",
        "Confidence Governance",
        "Scenario Assumption Version",
        "Scenario Route Status",
        "Canonical Allocation Status",
        "Allocation Available",
        "Selected Suppliers",
        "Allocation Shares",
        "Allocated Volumes",
        "Evidence Origin",
        "Human Review Required",
        "Legacy Fallback Used",
        "Blocking Reasons",
        "Analytical Leading Supplier",
        "Tooling Replacement Applied",
        "Already New Tooling",
        "Tooling Not Applicable",
    }
    assert required.issubset(scenarios.columns)
    assert "Standard Allocation Status" not in scenarios.columns
    assert "Optimized Allocation Status" not in scenarios.columns


def test_non_applicable_and_blocked_scenario_exports_are_fail_closed():
    _, _, _, _, scenarios = _outputs()
    metpet = scenarios.loc[scenarios["Scenario"] == "MetPET Availability Stress"].iloc[0]
    assert metpet["Scenario Applicable"] == False
    assert metpet["Scenario Route Status"] == "NOT_APPLICABLE"
    assert metpet["Canonical Allocation Status"] == "No allocation"
    assert metpet["Allocation Available"] == False
    assert metpet["Selected Suppliers"] == ""
    capacity = scenarios.loc[scenarios["Scenario"] == "Press and Lamination Capacity Stress"].iloc[0]
    assert capacity["Canonical Allocation Status"] == "No allocation"
    assert capacity["Allocation Available"] == False
    assert capacity["Scenario Route Status"] not in {"READY", "WARNING"}
    assert capacity["Selected Suppliers"] == ""
    assert capacity["Blocking Reasons"]


def test_supplier_export_preserves_visible_eligibility_tco_units_and_disclaimer():
    assumptions, _, scored, _, _ = _outputs()
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


def test_c2_manifest_exposes_one_canonical_allocation_authority():
    _, _, scored, canonical, scenarios = _outputs()
    manifest = build_c2_export_manifest(scored, canonical, scenarios)
    eligible = scored[scored["technical_eligible"]]
    assert manifest["export_contract_version"] == C2_EXPORT_CONTRACT_VERSION
    assert manifest["analytical_leading_supplier"] == eligible.iloc[0]["Supplier"]
    assert manifest["canonical_allocation"] == canonical.to_dict(orient="records")
    assert len(manifest["scenario_allocations"]) == len(scenarios) == 7
    assert manifest["human_review_required"] is True
    assert manifest["legacy_fallback_used"] is False
    assert "visible_winner" not in manifest
    assert "standard_allocation" not in manifest
    assert "optimized_allocation" not in manifest


def test_c2_workbook_contains_only_canonical_allocation_sheets_and_exact_values():
    _, _, scored, canonical, scenarios = _outputs()
    manifest = build_c2_export_manifest(scored, canonical, scenarios)
    should_cost = pd.DataFrame([{"Component": "Controlled placeholder", "Unit Cost USD": 1.0}])
    workbook = build_excel_workbook(
        scored,
        should_cost,
        canonical,
        scenarios,
        display_currency="USD",
        fx_rate=83,
        annual_volume=500000,
        annual_volume_unit="kg",
        c2_manifest=manifest,
    )
    sheets = pd.ExcelFile(BytesIO(workbook)).sheet_names
    assert {"Canonical Allocation", "Scenario Allocations", "Scenarios", "C2 Governance"}.issubset(sheets)
    assert "Allocation" not in sheets
    assert "Standard Allocation" not in sheets
    assert "Optimized Allocation" not in sheets

    exported = pd.read_excel(BytesIO(workbook), sheet_name="Canonical Allocation")
    identity_columns = (
        "Supplier",
        "Recommended Allocation %",
        "Role",
        "Allocated Volume",
        "Capacity Utilization %",
        "Evidence Origin",
        "Route Status",
    )
    for column in identity_columns:
        assert column in canonical.columns
        assert column in exported.columns
        assert exported[column].tolist() == canonical[column].tolist()
    assert "Estimated Annual TCO USD" in canonical.columns
    assert "Estimated Annual TCO (USD)" in exported.columns
    assert exported["Estimated Annual TCO (USD)"].tolist() == canonical["Estimated Annual TCO USD"].tolist()


def test_live_app_uses_canonical_c2_export_wiring_only():
    source = Path("app.py").read_text(encoding="utf-8")
    canonical_manifest_call = """build_c2_export_manifest(
        scored_df,
        allocation_df,
        scenario_df,
    )"""
    assert canonical_manifest_call in source
    assert "allocation_df,\n        allocation_df,\n        scenario_df" not in source
    assert "optimized_allocation_df=allocation_df" not in source
    assert source.count("c2_manifest=c2_manifest") == 2


def test_live_c2_excel_and_json_packages_share_governed_manifest():
    _, _, scored, canonical, scenarios = _outputs()
    manifest = build_c2_export_manifest(scored, canonical, scenarios)
    should_cost = pd.DataFrame([{"Component": "Controlled placeholder", "Unit Cost USD": 1.0}])
    workbook = build_excel_workbook(
        scored,
        should_cost,
        canonical,
        scenarios,
        display_currency="USD",
        fx_rate=83,
        annual_volume=500000,
        annual_volume_unit="kg",
        c2_manifest=manifest,
    )
    canonical_sheet = pd.read_excel(BytesIO(workbook), sheet_name="Canonical Allocation")
    scenario_sheet = pd.read_excel(BytesIO(workbook), sheet_name="Scenario Allocations")
    governance_sheet = pd.read_excel(BytesIO(workbook), sheet_name="C2 Governance")
    assert canonical_sheet["Supplier"].tolist() == canonical["Supplier"].tolist()
    assert len(scenario_sheet) == len(scenarios)
    assert set(governance_sheet["Field"]) >= {
        "export_contract_version",
        "selected_structure",
        "commercial_basis",
        "comparison_unit",
        "analytical_leading_supplier",
        "eligible_supplier_count",
        "canonical_allocation",
        "scenario_allocations",
        "scenario_assumption_versions",
        "human_review_required",
        "legacy_fallback_used",
        "disclaimer",
        "schema_migration_note",
    }

    eligible = scored[scored["technical_eligible"]]
    payload = json.loads(
        build_decision_package_json(
            eligible.iloc[0],
            {"estimated_ebitda_opportunity_usd": 0.0},
            canonical,
            scenarios,
            {"annual_saving_usd": 0.0},
            {"status": "Human Review Required"},
            c2_manifest=manifest,
        ).decode("utf-8")
    )
    exported_manifest = payload["flexible_laminates_governance"]
    assert json.dumps(exported_manifest, sort_keys=True, allow_nan=False) == json.dumps(
        manifest,
        sort_keys=True,
        allow_nan=False,
    )
    assert payload["canonical_allocation"] == manifest["canonical_allocation"]
    assert payload["scenario_allocations"] == manifest["scenario_allocations"]
    assert "allocation" not in payload
    assert "standard_allocation" not in exported_manifest
    assert "optimized_allocation" not in exported_manifest


def test_non_c2_json_export_remains_backward_compatible():
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
    assert "allocation" in payload
    assert "scenarios" in payload


def test_existing_category_data_routes_remain_unchanged():
    corrugated = get_demo_data("Packaging Procurement", "Corrugated Board")
    kraft = get_demo_data("Raw Material Procurement", "Kraft Paper")
    pet = get_demo_data("Raw Material Procurement", "PET Resin")
    assert set(corrugated["Unit"]) == {"piece"}
    assert set(kraft["Material"]) == {"Kraft Paper"}
    assert set(pet["Material"]) == {"PET Resin"}
