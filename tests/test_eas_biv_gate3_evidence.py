from io import BytesIO
import json

from openpyxl import Workbook

from modules.evidence_assurance import assure_excel_evidence, assure_json_evidence, steel_sheet_contract
from modules.export_evidence_registry import EXPORT_EVIDENCE, STEEL_EXCEL_LOCATIONS


def _workbook_bytes(sheet_names):
    workbook = Workbook()
    workbook.remove(workbook.active)
    for name in sheet_names:
        workbook.create_sheet(name)
    stream = BytesIO()
    workbook.save(stream)
    return stream.getvalue()


def test_steel_nine_sheet_contract_is_exact():
    assert steel_sheet_contract() == STEEL_EXCEL_LOCATIONS
    assert steel_sheet_contract() == (
        "Supplier Scores Report",
        "Supplier Comparison",
        "Should Cost",
        "Allocation",
        "Standard Allocation",
        "Optimized Allocation",
        "Scenarios",
        "Audit Supplier Scores",
        "C3 Governance",
    )


def test_steel_excel_evidence_exact_match():
    result = assure_excel_evidence(_workbook_bytes(STEEL_EXCEL_LOCATIONS), "EXP-EV-003")
    assert result.classification == "exact_match"
    assert result.blocking_status == "clear"
    assert result.missing_locations == ()
    assert result.schema_change is False
    assert result.audience == "business-and-audit"


def test_missing_excel_sheet_fails_closed():
    result = assure_excel_evidence(_workbook_bytes(STEEL_EXCEL_LOCATIONS[:-1]), "EXP-EV-003")
    assert result.classification == "export_path_inconsistency"
    assert result.blocking_status == "blocked"
    assert result.missing_locations == ("C3 Governance",)


def test_c2_governance_sheet_is_registered_and_checked():
    result = assure_excel_evidence(_workbook_bytes(("Scenarios", "C2 Governance")), "EXP-EV-005")
    assert result.classification == "exact_match"
    assert result.present_locations == ("Scenarios", "C2 Governance")


def test_canonical_c2_allocation_sheets_are_registered_and_checked():
    result = assure_excel_evidence(
        _workbook_bytes(("Canonical Allocation", "Scenario Allocations")),
        "EXP-EV-004",
    )
    assert result.classification == "exact_match"
    assert result.present_locations == ("Canonical Allocation", "Scenario Allocations")
    assert result.schema_change is True


def test_c2_json_registered_paths_exist():
    payload = {
        "recommended_supplier": {},
        "value_metrics": {},
        "canonical_allocation": [],
        "scenarios": [],
        "scenario_allocations": [],
        "negotiation": {},
        "eligibility": {},
        "flexible_laminates_governance": {
            "export_contract_version": "AIPC-MULTI-ALLOC-EXPORT-1.0",
            "canonical_allocation": [],
            "scenario_allocations": [],
            "human_review_required": True,
            "legacy_fallback_used": False,
        },
    }
    result = assure_json_evidence(json.dumps(payload), "EXP-EV-006")
    assert result.classification == "exact_match"
    assert result.blocking_status == "clear"
    assert result.schema_change is True


def test_steel_json_registered_paths_exist():
    payload = {
        "steel_governance": {
            "winner": "Supplier A",
            "winner_state": "Eligible",
            "human_approval_required": True,
            "scenarios": [],
        }
    }
    result = assure_json_evidence(payload, "EXP-EV-007")
    assert result.classification == "exact_match"
    assert result.missing_locations == ()


def test_missing_json_path_fails_closed():
    payload = {"steel_governance": {"winner": "Supplier A"}}
    result = assure_json_evidence(payload, "EXP-EV-007")
    assert result.classification == "export_path_inconsistency"
    assert result.blocking_status == "blocked"
    assert "steel_governance.scenarios" in result.missing_locations


def test_only_authorized_c2_evidence_entries_record_schema_change():
    assert EXPORT_EVIDENCE
    changed = {item.evidence_id for item in EXPORT_EVIDENCE if item.schema_change}
    assert changed == {"EXP-EV-004", "EXP-EV-006"}
    assert all(
        item.schema_change is False
        for item in EXPORT_EVIDENCE
        if item.evidence_id not in changed
    )


def test_registered_serializer_functions_are_exact():
    by_id = {item.evidence_id: item for item in EXPORT_EVIDENCE}
    assert by_id["EXP-EV-006"].source_function == "build_decision_package_json"
    assert by_id["EXP-EV-007"].source_function == "build_steel_governance_manifest; build_steel_json_export"
    assert "build_steel_decision_package_json" not in by_id["EXP-EV-007"].source_function
