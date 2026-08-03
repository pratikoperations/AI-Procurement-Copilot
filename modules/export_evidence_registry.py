"""Read-only map from calculation IDs to existing export locations."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ExportEvidence:
    evidence_id: str
    export_type: str
    location: str
    category_applicability: Tuple[str, ...]
    calculation_ids: Tuple[str, ...]
    audience: str
    source_file: str
    source_function: str
    schema_change: bool = False


STEEL_EXCEL_LOCATIONS = (
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

EXPORT_EVIDENCE = (
    ExportEvidence("EXP-EV-001", "excel", "Supplier Scores Report; Audit Supplier Scores", ("Packaging", "Raw materials"), ("SCR-001", "PER-001", "ESG-001", "RSK-001"), "business-and-audit", "modules/exports.py", "build_excel_workbook"),
    ExportEvidence("EXP-EV-002", "excel", "Should Cost", ("PET Resin", "Kraft Paper", "Corrugated Board", "Flexible Laminates"), ("PET-001", "KRF-001", "COR-001", "LAM-004"), "business-facing", "modules/exports.py", "build_excel_workbook"),
    ExportEvidence("EXP-EV-003", "excel", "; ".join(STEEL_EXCEL_LOCATIONS), ("Steel",), ("STL-001", "STL-002", "STL-003", "SCR-002", "ALC-001", "ALC-002", "SCN-003"), "business-and-audit", "modules/steel_exports.py", "build_steel_excel_workbook"),
    ExportEvidence("EXP-EV-004", "excel", "Canonical Allocation; Scenario Allocations", ("Flexible Laminates",), ("ALC-001", "ALC-002", "SCN-001", "SCN-002"), "business-facing", "modules/exports.py", "build_excel_workbook", schema_change=True),
    ExportEvidence("EXP-EV-005", "excel", "Scenarios; C2 Governance", ("Packaging", "Raw materials", "Flexible Laminates"), ("SCN-001", "SCN-002"), "business-and-audit", "modules/exports.py", "build_excel_workbook"),
    ExportEvidence("EXP-EV-006", "json", "recommended_supplier; value_metrics; canonical_allocation; scenarios; scenario_allocations; negotiation; eligibility; flexible_laminates_governance.export_contract_version; flexible_laminates_governance.canonical_allocation; flexible_laminates_governance.scenario_allocations; flexible_laminates_governance.human_review_required; flexible_laminates_governance.legacy_fallback_used", ("Flexible Laminates",), ("SCR-001", "ALC-001", "ALC-002", "SCN-001", "SCN-002"), "audit-facing", "modules/exports.py", "build_decision_package_json", schema_change=True),
    ExportEvidence("EXP-EV-007", "json", "steel_governance.winner; steel_governance.winner_state; steel_governance.human_approval_required; steel_governance.scenarios", ("Steel",), ("SCR-002", "SCN-003", "STL-003"), "audit-facing", "modules/steel_exports.py", "build_steel_governance_manifest; build_steel_json_export"),
)
