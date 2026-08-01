"""Stable, read-only metadata for the Calculation & Assumption Explorer.

Formula strings are documentation only. They must never be evaluated to produce
business results; authoritative values continue to come from existing engines.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


HUMAN_REVIEW_BOUNDARY = (
    "Controlled decision-support evidence only. No autonomous award, engineering "
    "certification, live-market-data claim, production allocation or realized-savings claim."
)


@dataclass(frozen=True)
class CalculationDefinition:
    calculation_id: str
    business_name: str
    category: str
    formula_text: str
    variables: Tuple[str, ...]
    unit: str
    source_module: str
    downstream_outputs: Tuple[str, ...]
    governance_caveat: str = HUMAN_REVIEW_BOUNDARY


@dataclass(frozen=True)
class AssumptionDefinition:
    assumption_id: str
    business_name: str
    category: str
    key: str
    unit: str
    source_module: str
    editable: bool
    edit_scope: str
    validation_rules: Tuple[str, ...]
    governance_caveat: str = HUMAN_REVIEW_BOUNDARY


CALCULATIONS = (
    CalculationDefinition("COM-001", "Effective Annual Volume", "Cross-category", "annual_volume * (1 + demand_change)", ("annual_volume", "demand_change"), "category unit", "modules/category_cost_router.py", ("should_cost", "tco", "allocation", "exports")),
    CalculationDefinition("COM-002", "USD to INR Conversion", "Cross-category", "usd_value * fx_rate", ("usd_value", "fx_rate"), "INR", "modules/steel_cost.py; modules/utils.py", ("display", "excel", "json")),
    CalculationDefinition("COM-003", "Annual Value", "Cross-category", "unit_value * annual_volume", ("unit_value", "annual_volume"), "currency/year", "category cost and export modules", ("dashboard", "excel", "json")),
    CalculationDefinition("KRF-001", "Kraft Paper Target Unit Cost", "Kraft Paper", "sum(adjusted governed cost components)", ("kraft_variant", "kraft_gsm", "kraft_strength_grade", "raw_material_shock", "freight_shock"), "USD/kg", "modules/raw_material_cost.py", ("should_cost", "recommendation", "exports"), "GSM premium represents controlled profile availability, not physical mass consumption."),
    CalculationDefinition("LAM-001", "Flexible Laminates Substrate Cost", "Flexible Laminates", "sum(material_share * substrate_price * (1 + raw_material_shock))", ("laminate_structure", "raw_material_shock"), "USD/kg", "modules/flexible_laminate_cost.py", ("should_cost", "scenario", "exports"), "Total micron is metadata only; fixed synthetic mass-share profiles are authoritative."),
    CalculationDefinition("LAM-002", "Flexible Laminates Compounded Yield", "Flexible Laminates", "(1-print_loss)*(1-lamination_loss)*(1-slitting_loss)", ("laminate_printing_loss_pct", "laminate_lamination_loss_pct", "laminate_slitting_loss_pct"), "factor", "modules/flexible_laminate_cost.py", ("process_loss_cost", "target_unit_cost")),
    CalculationDefinition("LAM-003", "Flexible Laminates Tooling Amortisation", "Flexible Laminates", "colours * tooling_cost_per_colour / tooling_lifetime_volume", ("laminate_number_of_colours", "laminate_tooling_cost_per_colour_usd", "laminate_tooling_lifetime_volume_kg", "laminate_tooling_status"), "USD/kg", "modules/flexible_laminate_cost.py", ("should_cost", "tooling_scenario", "exports")),
    CalculationDefinition("LAM-004", "Flexible Laminates Target Unit Cost", "Flexible Laminates", "gross_recurring + tooling + freight + supplier_margin", ("components",), "USD/kg", "modules/flexible_laminate_cost.py", ("recommendation", "scenario", "exports")),
    CalculationDefinition("STL-001", "Steel Recurring Gross Cost", "Steel", "recurring_net / (yield_pct / 100)", ("steel components", "steel_yield_pct"), "USD/kg", "modules/steel_cost.py", ("yield_loss_effect", "landed_pre_duty")),
    CalculationDefinition("STL-002", "Steel Import Duty", "Steel", "landed_pre_duty * import_duty_pct / 100 when sourcing_route == Import", ("steel_sourcing_route", "steel_import_duty_pct"), "USD/kg", "modules/steel_cost.py", ("target_unit_cost", "exports")),
    CalculationDefinition("STL-003", "Steel Target Unit Cost", "Steel", "landed_pre_duty + import_duty + supplier_margin", ("steel components", "steel_yield_pct", "steel_import_duty_pct", "steel_supplier_margin_pct"), "USD/kg", "modules/steel_cost.py", ("steel scoring", "scenarios", "allocation", "exports")),
    CalculationDefinition("TCO-001", "Packaging Risk-Adjusted TCO", "Generic", "scenario_price + freight + inventory + working_capital + risk_penalty + lead_time_buffer", ("quoted_price", "annual_volume", "raw_material_shock", "freight_shock", "demand_change"), "USD/unit", "modules/tco.py", ("supplier scoring", "recommendation", "allocation", "exports")),
    CalculationDefinition("TCO-002", "Raw-Material Risk-Adjusted TCO", "Raw Material", "authoritative raw-material TCO engine output", ("supplier row", "annual_volume", "scenario assumptions"), "USD/kg", "modules/raw_material_tco.py", ("supplier scoring", "recommendation", "allocation", "exports")),
    CalculationDefinition("RSK-001", "Supplier Risk Resilience", "Generic", "normalize(100 - sum(risk penalties))", ("payment", "incoterm", "lead_time", "moq", "otif", "quality_ppm"), "score/100", "modules/risk.py", ("tco", "supplier scoring", "allocation")),
    CalculationDefinition("SCR-001", "Generic Weighted Supplier Score", "Generic", "sum(normalized factor score * category weight)", ("tco_score", "risk_score", "lead_time_score", "payment_score", "moq_score", "performance_score", "esg_score"), "score/100", "modules/scoring.py", ("ranking", "recommendation", "allocation")),
    CalculationDefinition("SCR-002", "Governed Steel Supplier Score", "Steel", "authoritative governed Steel scoring output", ("steel supplier evidence", "steel profile", "substitution state"), "score/100", "modules/steel_risk.py; modules/scoring.py", ("steel recommendation", "steel allocation", "steel scenarios")),
    CalculationDefinition("ALC-001", "Standard Allocation", "Generic", "threshold and capacity constrained allocation", ("annual_volume", "max_supplier_share", "min_backup_share", "min_risk_score", "min_esg_score"), "% and category unit", "modules/allocation.py", ("decision", "excel", "json")),
    CalculationDefinition("ALC-002", "Optimized Allocation", "Generic", "deterministic supported split selected from score gap, risk, performance and capacity", ("scored suppliers", "annual_volume"), "% and category unit", "modules/allocation_optimizer.py", ("decision", "excel", "json")),
    CalculationDefinition("SCN-001", "Generic Procurement Scenario", "Generic", "apply controlled scenario mutation then rerun existing engines", ("procurement_intelligence_scenario",), "scenario result", "modules/scenario_engine.py", ("scoring", "allocation", "decision")),
    CalculationDefinition("SCN-002", "Flexible Laminates Governed Scenario", "Flexible Laminates", "apply one controlled C2 scenario then rerun existing engines", ("laminate structure", "scenario"), "scenario result", "modules/scenario_engine.py", ("scoring", "allocation", "decision", "exports")),
    CalculationDefinition("SCN-003", "Steel Governed Scenario", "Steel", "consume dedicated Steel scenario engine output", ("steel_governed_scenario",), "scenario result", "modules/steel_scenario.py; modules/steel_ux.py", ("steel decision", "steel allocation", "steel exports")),
    CalculationDefinition("EXP-001", "Excel Evidence Package", "Cross-category", "serialize authoritative result tables without recalculation", ("scores", "should_cost", "allocation", "scenarios"), "xlsx", "modules/exports.py; modules/steel_exports.py", ("audit evidence",)),
    CalculationDefinition("EXP-002", "JSON Decision Audit", "Cross-category", "strict-JSON normalization of authoritative outputs", ("decision package",), "json", "modules/exports.py; modules/steel_exports.py", ("audit evidence",)),
)


ASSUMPTIONS = (
    AssumptionDefinition("COM-A01", "Annual Volume", "Cross-category", "annual_volume", "category unit", "modules/sidebar.py", True, "controlled", ("positive",)),
    AssumptionDefinition("COM-A02", "USD-INR FX Rate", "Cross-category", "fx_rate", "INR/USD", "modules/sidebar.py", True, "controlled", ("finite", "greater than zero")),
    AssumptionDefinition("COM-A03", "Display Currency", "Cross-category", "display_currency", "mode", "modules/sidebar.py", True, "controlled", ("USD, INR or Both",)),
    AssumptionDefinition("KRF-A01", "Fibre Basis", "Kraft Paper", "kraft_variant", "profile", "modules/sidebar.py", True, "controlled", ("Recycled Kraft or Virgin Kraft",)),
    AssumptionDefinition("KRF-A02", "GSM", "Kraft Paper", "kraft_gsm", "gsm", "modules/sidebar.py", True, "controlled", ("whole number", "120, 150 or 180")),
    AssumptionDefinition("KRF-A03", "Strength Grade", "Kraft Paper", "kraft_strength_grade", "BF", "modules/sidebar.py", True, "controlled", ("18 BF, 22 BF or 28 BF",)),
    AssumptionDefinition("LAM-A01", "Laminate Structure", "Flexible Laminates", "laminate_structure", "profile", "modules/sidebar.py", True, "controlled", ("supported governed structure",)),
    AssumptionDefinition("LAM-A02", "Total Micron", "Flexible Laminates", "laminate_total_micron", "micron", "modules/sidebar.py", True, "controlled", ("35 to 140",), "Metadata only; not a physical mass inference."),
    AssumptionDefinition("LAM-A03", "Printing Loss", "Flexible Laminates", "laminate_printing_loss_pct", "%", "modules/sidebar.py", True, "controlled", ("0 to 8",)),
    AssumptionDefinition("LAM-A04", "Lamination Loss", "Flexible Laminates", "laminate_lamination_loss_pct", "%", "modules/sidebar.py", True, "controlled", ("0 to 6",)),
    AssumptionDefinition("LAM-A05", "Slitting Loss", "Flexible Laminates", "laminate_slitting_loss_pct", "%", "modules/sidebar.py", True, "controlled", ("0 to 5", "combined effective loss below 15%")),
    AssumptionDefinition("STL-A01", "Steel Profile", "Steel", "steel_profile", "profile", "modules/steel_ux.py", True, "controlled", ("CR, GI Z120 or PPGI Z120 governed profile",)),
    AssumptionDefinition("STL-A02", "Sourcing Route", "Steel", "steel_sourcing_route", "route", "modules/steel_ux.py", True, "controlled", ("Domestic or Import",)),
    AssumptionDefinition("STL-A03", "Zinc Cost", "Steel", "steel_zinc_cost_usd_per_kg", "USD/kg", "modules/steel_ux.py", True, "controlled", ("profile applicable", "finite", "non-negative")),
    AssumptionDefinition("STL-A04", "Paint or Treatment Cost", "Steel", "steel_paint_treatment_usd_per_kg", "USD/kg", "modules/steel_ux.py", True, "controlled", ("profile applicable", "finite", "non-negative")),
    AssumptionDefinition("STL-A05", "Import Duty", "Steel", "steel_import_duty_pct", "%", "modules/steel_ux.py", True, "controlled", ("0 to 100", "zero for Domestic")),
    AssumptionDefinition("STL-A06", "Steel Yield", "Steel", "steel_yield_pct", "%", "modules/steel_cost.py", False, "none", ("greater than zero", "no more than 100")),
    AssumptionDefinition("STL-A07", "Steel Supplier Margin", "Steel", "steel_supplier_margin_pct", "%", "modules/steel_cost.py", False, "none", ("0 to below 100",)),
    AssumptionDefinition("GEN-A01", "Raw Material Shock", "Generic", "raw_material_shock", "fraction", "modules/sidebar.py", True, "scenario", ("controlled slider range",)),
    AssumptionDefinition("GEN-A02", "Freight Shock", "Generic", "freight_shock", "fraction", "modules/sidebar.py", True, "scenario", ("controlled slider range",)),
    AssumptionDefinition("GEN-A03", "Demand Change", "Generic", "demand_change", "fraction", "modules/sidebar.py", True, "scenario", ("controlled slider range",)),
    AssumptionDefinition("ALC-A01", "Maximum Supplier Share", "Generic", "max_supplier_share", "%", "modules/sidebar.py", True, "controlled", ("0 to 100",)),
    AssumptionDefinition("ALC-A02", "Minimum Backup Share", "Generic", "min_backup_share", "%", "modules/sidebar.py", True, "controlled", ("0 to 100",)),
    AssumptionDefinition("ALC-A03", "Minimum Risk Score", "Generic", "min_risk_score", "score/100", "modules/sidebar.py", True, "controlled", ("0 to 100",)),
    AssumptionDefinition("ALC-A04", "Minimum ESG Score", "Generic", "min_esg_score", "score/100", "modules/sidebar.py", True, "controlled", ("0 to 100",)),
)


EXCEL_EVIDENCE_MAP = {
    "SCR-001": "Supplier Scores Report; Audit Supplier Scores",
    "SCR-002": "Supplier Comparison; Audit Supplier Scores",
    "KRF-001": "Should Cost",
    "LAM-004": "Should Cost; C2 Governance",
    "STL-003": "Steel Should Cost",
    "ALC-001": "Allocation; Standard Allocation",
    "ALC-002": "Optimized Allocation",
    "SCN-001": "Scenarios",
    "SCN-002": "Scenarios; C2 Governance",
    "SCN-003": "Steel Scenarios",
}

JSON_EVIDENCE_MAP = {
    "SCR-001": "recommended_supplier; value_metrics",
    "SCR-002": "steel_governance.recommendation",
    "ALC-001": "allocation",
    "ALC-002": "optimized_allocation",
    "SCN-001": "scenarios",
    "SCN-002": "flexible_laminates_governance.scenarios",
    "SCN-003": "steel_governance.scenarios",
}


def calculation_by_id(calculation_id: str) -> CalculationDefinition:
    return next(item for item in CALCULATIONS if item.calculation_id == calculation_id)


def assumption_by_key(key: str) -> AssumptionDefinition | None:
    return next((item for item in ASSUMPTIONS if item.key == key), None)
