"""Governed Gate 3 cross-category reconciliation coverage registry."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReconciliationCoverage:
    coverage_id: str
    domain: str
    category: str
    calculation_id: str
    formula_id: str
    source_module: str
    source_function: str
    comparison_kind: str
    status: str = "active"


RECONCILIATION_COVERAGE = (
    ReconciliationCoverage("REC-PET", "should_cost", "PET Resin", "PET-001", "F-RM-SHOULDCOST", "modules/raw_material_cost.py", "calculate_raw_material_should_cost", "authoritative_output"),
    ReconciliationCoverage("REC-KRF", "should_cost", "Kraft Paper", "KRF-001", "F-RM-SHOULDCOST", "modules/raw_material_cost.py", "calculate_raw_material_should_cost", "authoritative_output"),
    ReconciliationCoverage("REC-COR", "should_cost", "Corrugated Board", "COR-001", "F-PKG-SHOULDCOST", "modules/should_cost.py", "calculate_packaging_should_cost", "authoritative_output"),
    ReconciliationCoverage("REC-LAM", "should_cost", "Flexible Laminates", "LAM-004", "F-C2-SHOULDCOST", "modules/flexible_laminate_cost.py", "calculate_flexible_laminate_should_cost", "authoritative_output"),
    ReconciliationCoverage("REC-STL", "should_cost", "Steel", "STL-003", "F-C3-SHOULDCOST", "modules/steel_cost.py", "calculate_steel_should_cost", "authoritative_output"),
    ReconciliationCoverage("REC-TCO-PKG", "tco", "Packaging", "TCO-001", "F-TCO-PKG", "modules/tco.py", "calculate_supplier_tco", "authoritative_output"),
    ReconciliationCoverage("REC-TCO-RM", "tco", "Raw materials", "TCO-002", "F-TCO-RM", "modules/raw_material_tco.py", "calculate_raw_material_tco", "authoritative_output"),
    ReconciliationCoverage("REC-RISK-GEN", "risk", "Generic", "RSK-001", "F-RISK-GEN", "modules/risk.py", "calculate_risk", "authoritative_output"),
    ReconciliationCoverage("REC-RISK-C2", "risk", "Flexible Laminates", "RSK-002", "F-RISK-GEN", "modules/flexible_laminate_risk.py", "calculate_flexible_laminate_risk", "authoritative_output"),
    ReconciliationCoverage("REC-RISK-C3", "risk", "Steel", "RSK-003", "F-SCORE-STEEL", "modules/steel_risk.py", "score_and_recommend_steel_suppliers", "authoritative_output"),
    ReconciliationCoverage("REC-SCORE-GEN", "scoring", "Packaging and Raw materials", "SCR-001", "F-SCORE-GEN", "modules/scoring.py", "enrich_supplier_scores", "weighted_contribution"),
    ReconciliationCoverage("REC-SCORE-C3", "scoring", "Steel", "SCR-002", "F-SCORE-STEEL", "modules/steel_risk.py", "score_and_recommend_steel_suppliers", "weighted_contribution"),
    ReconciliationCoverage("REC-PER", "performance", "Packaging and Raw materials", "PER-001", "F-PERFORMANCE", "modules/performance.py", "calculate_performance_score", "weighted_contribution"),
    ReconciliationCoverage("REC-ESG", "esg", "Packaging and Raw materials", "ESG-001", "F-ESG", "modules/esg.py", "calculate_esg_score", "weighted_contribution"),
    ReconciliationCoverage("REC-TECH", "technical_eligibility", "Cross-category", "ELG-TECH", "F-ELIGIBILITY", "modules/scoring.py", "enrich_supplier_scores", "blocking_status"),
    ReconciliationCoverage("REC-ELG", "recommendation_eligibility", "All", "ELG-001", "F-ELIGIBILITY", "modules/recommendation_eligibility.py", "evaluate_recommendation_eligibility", "blocking_status"),
    ReconciliationCoverage("REC-ALLOC-STD", "allocation", "Generic", "ALC-001", "F-ALLOC-STD", "modules/allocation.py", "recommend_allocation", "allocation"),
    ReconciliationCoverage("REC-ALLOC-OPT", "allocation", "Generic", "ALC-002", "F-ALLOC-OPT", "modules/allocation_optimizer.py", "optimize_allocation", "allocation"),
    ReconciliationCoverage("REC-SCN-GEN", "scenario", "Generic", "SCN-001", "F-SCENARIO-GENERIC", "modules/scenario_engine.py", "run_intelligence_scenario", "scenario_output"),
    ReconciliationCoverage("REC-SCN-C2", "scenario", "Flexible Laminates", "SCN-002", "F-SCENARIO-C2", "modules/scenario_engine.py", "run_all_flexible_laminate_scenarios", "scenario_output"),
    ReconciliationCoverage("REC-SCN-C3", "scenario", "Steel", "SCN-003", "F-SCENARIO-STEEL", "modules/steel_scenario.py", "run_governed_steel_scenarios", "scenario_output"),
    ReconciliationCoverage("REC-EXCEL", "export", "All", "EXP-EXCEL", "F-EXPORT-EXCEL", "modules/exports.py; modules/steel_exports.py", "build_excel_workbook; build_steel_excel_workbook", "excel_evidence"),
    ReconciliationCoverage("REC-JSON", "export", "All", "EXP-JSON", "F-EXPORT-JSON", "modules/exports.py; modules/steel_exports.py", "build_decision_package_json; build_steel_governance_manifest; build_steel_json_export", "json_evidence"),
)
