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


EXPORT_EVIDENCE = (
    ExportEvidence("EXP-EV-001", "excel", "Supplier Scores Report; Audit Supplier Scores", ("Packaging", "Raw materials"), ("SCR-001", "PER-001", "ESG-001", "RSK-001"), "business-and-audit", "modules/exports.py", "build_excel_workbook"),
    ExportEvidence("EXP-EV-002", "excel", "Should Cost", ("PET Resin", "Kraft Paper", "Corrugated Board", "Flexible Laminates"), ("PET-001", "KRF-001", "COR-001", "LAM-004"), "business-facing", "modules/exports.py", "build_excel_workbook"),
    ExportEvidence("EXP-EV-003", "excel", "Steel Should Cost", ("Steel",), ("STL-001", "STL-002", "STL-003"), "business-and-audit", "modules/steel_exports.py", "build_steel_excel_workbook"),
    ExportEvidence("EXP-EV-004", "excel", "Allocation; Standard Allocation; Optimized Allocation", ("All",), ("ALC-001", "ALC-002"), "business-facing", "modules/exports.py", "build_excel_workbook"),
    ExportEvidence("EXP-EV-005", "excel", "Scenarios; C2 Governance; Steel Scenarios", ("All",), ("SCN-001", "SCN-002", "SCN-003"), "business-and-audit", "modules/exports.py; modules/steel_exports.py", "build_excel_workbook; build_steel_excel_workbook"),
    ExportEvidence("EXP-EV-006", "json", "recommended_supplier; value_metrics; allocation; optimized_allocation; scenarios", ("Packaging", "Raw materials"), ("SCR-001", "ALC-001", "ALC-002", "SCN-001", "SCN-002"), "audit-facing", "modules/exports.py", "build_decision_package_json"),
    ExportEvidence("EXP-EV-007", "json", "steel_governance.recommendation; steel_governance.scenarios", ("Steel",), ("SCR-002", "SCN-003", "STL-003"), "audit-facing", "modules/steel_exports.py", "build_steel_decision_package_json"),
)
