"""Versioned, read-only metadata for calculation explainability.

Expressions are documentation only. Authoritative business values always come
from existing procurement engines and are never evaluated from this registry.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Tuple

HUMAN_REVIEW_BOUNDARY = (
    "Controlled portfolio decision support only. Human approval is mandatory; "
    "no autonomous award, production allocation, engineering certification, "
    "live-market claim or realized-savings claim is permitted."
)
UNDOCUMENTED_DEFAULT = "existing undocumented controlled default"


@dataclass(frozen=True)
class FormulaDefinition:
    formula_id: str
    version: str
    business_name: str
    description: str
    category_applicability: Tuple[str, ...]
    source_file: str
    source_function: str
    input_definitions: Tuple[str, ...]
    input_units: Tuple[str, ...]
    expression: str
    intermediate_steps: Tuple[str, ...]
    output_definition: str
    output_unit: str
    owner: str = "Procurement decision-support owner"
    status: str = "active"
    effective_date: str | None = None
    governance_notes: str = HUMAN_REVIEW_BOUNDARY


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
    formula_id: str
    formula_version: str = "1.0"
    description: str = "Authoritative deterministic application result."
    source_function: str = ""
    owner: str = "Procurement decision-support owner"
    status: str = "active"
    effective_date: str | None = None
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
    default_reference: Any = None
    original_unit: str | None = None
    supplier_scope: str | None = None
    rfq_scenario_scope: str | None = None
    source_level: str = "category_default"
    evidence_classification: str = UNDOCUMENTED_DEFAULT
    source_reference: str | None = None
    effective_date: str | None = None
    review_expiry_date: str | None = None
    confidence: float | None = None
    override_status: str = "not_overridden"
    override_reason: str | None = None
    approver: str | None = None
    version: str = "1.0"
    governance_caveat: str = HUMAN_REVIEW_BOUNDARY


FORMULAS = (
    FormulaDefinition("F-COM-VOLUME", "1.0", "Effective annual volume", "Apply governed demand change.", ("All",), "modules/category_cost_router.py", "calculate_category_should_cost", ("annual_volume", "demand_change"), ("category unit", "fraction"), "annual_volume * (1 + demand_change)", ("resolve annual volume", "apply demand factor"), "effective annual volume", "category unit"),
    FormulaDefinition("F-COM-FX", "1.0", "USD-INR conversion", "Display conversion only.", ("All",), "modules/steel_cost.py", "steel_should_cost_dataframe", ("usd_value", "fx_rate"), ("USD", "INR/USD"), "usd_value * fx_rate", ("read governed FX", "multiply authoritative USD value"), "INR value", "INR"),
    FormulaDefinition("F-RM-SHOULDCOST", "1.0", "Raw-material should-cost", "Sum adjusted governed components.", ("PET Resin", "Kraft Paper", "Raw materials"), "modules/raw_material_cost.py", "calculate_raw_material_should_cost", ("commodity baseline", "commodity shock", "freight shock", "fx shock"), ("USD/kg", "fraction", "fraction", "fraction"), "sum(adjusted components)", ("resolve baseline", "apply allowed shocks", "sum components"), "target unit cost", "USD/kg"),
    FormulaDefinition("F-PKG-SHOULDCOST", "1.0", "Generic packaging should-cost", "Sum generic packaging components.", ("Corrugated Board", "Generic packaging"), "modules/should_cost.py", "calculate_packaging_should_cost", ("component defaults", "raw-material shock", "freight shock", "fx shock"), ("USD/unit", "fraction", "fraction", "fraction"), "sum(adjusted components) * (1 + fx_shock)", ("adjust material", "adjust freight", "sum", "apply FX shock"), "target unit cost", "USD/unit"),
    FormulaDefinition("F-C2-SHOULDCOST", "1.0", "Flexible Laminates should-cost", "Governed substrate, process-loss, tooling, freight and margin model.", ("Flexible Laminates",), "modules/flexible_laminate_cost.py", "calculate_flexible_laminate_should_cost", ("structure", "print profile", "process losses", "tooling", "shocks"), ("profile", "profile", "%", "USD/kg", "fraction"), "authoritative C2 component reconciliation", ("substrate", "conversion", "compounded yield", "tooling", "freight", "margin"), "target unit cost", "USD/kg"),
    FormulaDefinition("F-C3-SHOULDCOST", "1.0", "Steel should-cost", "Governed Steel profile and route calculation.", ("Steel",), "modules/steel_cost.py", "calculate_steel_should_cost", ("steel components", "yield", "route", "duty", "margin"), ("USD/kg", "%", "route", "%", "%"), "authoritative Steel component reconciliation", ("recurring net", "yield gross-up", "landed pre-duty", "duty", "margin"), "target unit cost", "USD/kg"),
    FormulaDefinition("F-TCO-PKG", "1.0", "Packaging risk-adjusted TCO", "Risk, inventory, freight and working-capital adjusted comparison.", ("Packaging",), "modules/tco.py", "calculate_supplier_tco", ("supplier row", "annual volume", "scenario assumptions"), ("mixed", "category unit", "mixed"), "scenario price + freight + inventory + working capital + risk penalty + lead buffer", ("scenario price", "freight", "inventory", "working capital", "risk", "lead buffer"), "adjusted TCO", "USD/unit"),
    FormulaDefinition("F-TCO-RM", "1.0", "Raw-material TCO", "Dedicated raw-material TCO service.", ("Raw materials",), "modules/raw_material_tco.py", "calculate_raw_material_tco", ("supplier row", "annual volume", "scenario assumptions"), ("mixed", "kg", "mixed"), "authoritative raw-material TCO service", ("resolve supplier inputs", "apply raw-material TCO service"), "adjusted TCO", "USD/kg"),
    FormulaDefinition("F-RISK-GEN", "1.0", "Generic supplier risk resilience", "Penalty-based supplier risk score.", ("Generic",), "modules/risk.py", "calculate_risk", ("payment", "incoterm", "lead time", "MOQ", "OTIF", "PPM"), ("terms", "term", "days", "unit", "%", "PPM"), "normalize(100 - sum(risk penalties))", ("calculate penalties", "sum penalties", "normalize", "assign band"), "risk resilience", "score/100"),
    FormulaDefinition("F-SCORE-GEN", "1.0", "Generic weighted supplier score", "Weighted category profile.", ("Packaging", "Raw materials"), "modules/scoring.py", "enrich_supplier_scores", ("normalized factors", "weight profile"), ("score/100", "fraction"), "sum(factor score * weight)", ("normalize factors", "apply profile", "round"), "total score", "score/100"),
    FormulaDefinition("F-SCORE-STEEL", "1.0", "Governed Steel supplier score", "Dedicated Steel scoring service.", ("Steel",), "modules/steel_risk.py", "score_and_recommend_steel_suppliers", ("supplier evidence", "profile", "substitution state"), ("mixed", "profile", "state"), "authoritative governed Steel score", ("technical eligibility", "governed risk", "governed score"), "governed total score", "score/100"),
    FormulaDefinition("F-ALLOC-STD", "1.0", "Standard allocation", "Threshold, capacity and concentration constrained allocation.", ("Generic",), "modules/allocation.py", "recommend_allocation", ("scored suppliers", "volume", "thresholds"), ("table", "category unit", "mixed"), "authoritative allocation rules", ("filter technical", "apply thresholds", "capacity", "concentration", "residual"), "allocation", "% and category unit"),
    FormulaDefinition("F-ALLOC-OPT", "1.0", "Optimized allocation", "Select from governed deterministic splits.", ("Generic",), "modules/allocation_optimizer.py", "optimize_allocation", ("scored suppliers", "volume"), ("table", "category unit"), "authoritative supported split selection", ("eligible suppliers", "candidate splits", "select governed split"), "optimized allocation", "% and category unit"),
    FormulaDefinition("F-ELIGIBILITY", "1.0", "Recommendation eligibility", "Validation, blocker and confidence gate.", ("All",), "modules/recommendation_eligibility.py", "evaluate_recommendation_eligibility", ("validation", "business rules", "confidence", "scores", "volume"), ("records", "records", "score/100", "table", "category unit"), "deterministic status ladder", ("blockers", "confidence thresholds", "conditions", "language permission"), "eligibility status", "status"),
)


def _calc(cid, name, category, formula, variables, unit, source, outputs, formula_id, function, note=HUMAN_REVIEW_BOUNDARY):
    return CalculationDefinition(cid, name, category, formula, variables, unit, source, outputs, formula_id, source_function=function, governance_caveat=note)


CALCULATIONS = (
    _calc("COM-001", "Effective Annual Volume", "Cross-category", "annual_volume * (1 + demand_change)", ("annual_volume", "demand_change"), "category unit", "modules/category_cost_router.py", ("should_cost", "tco", "allocation", "exports"), "F-COM-VOLUME", "calculate_category_should_cost"),
    _calc("COM-002", "USD to INR Conversion", "Cross-category", "usd_value * fx_rate", ("usd_value", "fx_rate"), "INR", "modules/steel_cost.py", ("display", "excel", "json"), "F-COM-FX", "steel_should_cost_dataframe"),
    _calc("COM-003", "Annual Value", "Cross-category", "unit_value * annual_volume", ("unit_value", "annual_volume"), "currency/year", "category dataframe/export services", ("dashboard", "excel", "json"), "F-COM-VOLUME", "category dataframe services"),
    _calc("PET-001", "PET Resin Target Unit Cost", "PET Resin", "sum(adjusted raw-material components)", ("commodity baseline", "shocks"), "USD/kg", "modules/raw_material_cost.py", ("should_cost", "recommendation", "exports"), "F-RM-SHOULDCOST", "calculate_raw_material_should_cost"),
    _calc("KRF-001", "Kraft Paper Target Unit Cost", "Kraft Paper", "sum(adjusted governed cost components)", ("kraft_variant", "kraft_gsm", "kraft_strength_grade", "raw_material_shock", "freight_shock"), "USD/kg", "modules/raw_material_cost.py", ("should_cost", "recommendation", "exports"), "F-RM-SHOULDCOST", "calculate_raw_material_should_cost", "GSM premium represents controlled profile availability, not physical mass consumption."),
    _calc("COR-001", "Corrugated Board Target Unit Cost", "Corrugated Board", "sum(adjusted generic packaging components)", ("packaging components", "shocks"), "USD/unit", "modules/should_cost.py", ("should_cost", "recommendation", "exports"), "F-PKG-SHOULDCOST", "calculate_packaging_should_cost"),
    _calc("LAM-001", "Flexible Laminates Substrate Cost", "Flexible Laminates", "sum(material share * price * shock)", ("laminate_structure", "raw_material_shock"), "USD/kg", "modules/flexible_laminate_cost.py", ("should_cost", "scenario", "exports"), "F-C2-SHOULDCOST", "calculate_flexible_laminate_should_cost", "Total micron is metadata only; fixed synthetic mass-share profiles are authoritative."),
    _calc("LAM-002", "Flexible Laminates Compounded Yield", "Flexible Laminates", "(1-print loss)*(1-lamination loss)*(1-slitting loss)", ("three process losses",), "factor", "modules/flexible_laminate_cost.py", ("process_loss_cost", "target_unit_cost"), "F-C2-SHOULDCOST", "calculate_flexible_laminate_should_cost"),
    _calc("LAM-003", "Flexible Laminates Tooling Amortisation", "Flexible Laminates", "colours * cost per colour / lifetime volume", ("colours", "tooling cost", "lifetime volume", "tooling status"), "USD/kg", "modules/flexible_laminate_cost.py", ("should_cost", "tooling_scenario", "exports"), "F-C2-SHOULDCOST", "calculate_flexible_laminate_should_cost"),
    _calc("LAM-004", "Flexible Laminates Target Unit Cost", "Flexible Laminates", "authoritative C2 component sum", ("components",), "USD/kg", "modules/flexible_laminate_cost.py", ("recommendation", "scenario", "exports"), "F-C2-SHOULDCOST", "calculate_flexible_laminate_should_cost"),
    _calc("STL-001", "Steel Recurring Gross Cost", "Steel", "recurring_net / yield", ("steel components", "yield"), "USD/kg", "modules/steel_cost.py", ("yield_loss", "landed cost"), "F-C3-SHOULDCOST", "calculate_steel_should_cost"),
    _calc("STL-002", "Steel Import Duty", "Steel", "landed_pre_duty * duty when Import", ("route", "duty"), "USD/kg", "modules/steel_cost.py", ("target_unit_cost", "exports"), "F-C3-SHOULDCOST", "calculate_steel_should_cost"),
    _calc("STL-003", "Steel Target Unit Cost", "Steel", "landed + duty + margin", ("components", "yield", "route", "margin"), "USD/kg", "modules/steel_cost.py", ("score", "scenario", "allocation", "exports"), "F-C3-SHOULDCOST", "calculate_steel_should_cost"),
    _calc("TCO-001", "Packaging Risk-Adjusted TCO", "Generic Packaging", "authoritative packaging TCO", ("supplier row", "volume", "scenario"), "USD/unit", "modules/tco.py", ("score", "recommendation", "allocation", "exports"), "F-TCO-PKG", "calculate_supplier_tco"),
    _calc("TCO-002", "Raw-Material Risk-Adjusted TCO", "Raw Material", "authoritative raw-material TCO", ("supplier row", "volume", "scenario"), "USD/kg", "modules/raw_material_tco.py", ("score", "recommendation", "allocation", "exports"), "F-TCO-RM", "calculate_raw_material_tco"),
    _calc("RSK-001", "Supplier Risk Resilience", "Generic", "normalize(100 - penalties)", ("payment", "incoterm", "lead", "MOQ", "OTIF", "PPM"), "score/100", "modules/risk.py", ("tco", "score", "allocation"), "F-RISK-GEN", "calculate_risk"),
    _calc("SCR-001", "Generic Weighted Supplier Score", "Generic", "sum(normalized factor * weight)", ("factor scores", "weight profile"), "score/100", "modules/scoring.py", ("ranking", "recommendation", "allocation"), "F-SCORE-GEN", "enrich_supplier_scores"),
    _calc("SCR-002", "Governed Steel Supplier Score", "Steel", "authoritative governed Steel score", ("Steel evidence", "profile", "substitution"), "score/100", "modules/steel_risk.py", ("recommendation", "allocation", "scenario"), "F-SCORE-STEEL", "score_and_recommend_steel_suppliers"),
    _calc("PER-001", "Quality and Performance Score", "Generic", "authoritative performance service", ("quality and service fields",), "score/100", "modules/performance.py", ("weighted score", "recommendation"), "F-SCORE-GEN", "calculate_performance_score"),
    _calc("ESG-001", "ESG Score", "Generic", "authoritative ESG service", ("ESG fields",), "score/100", "modules/esg.py", ("weighted score", "allocation"), "F-SCORE-GEN", "calculate_esg_score"),
    _calc("ELG-001", "Technical Eligibility", "Cross-category", "authoritative category eligibility", ("technical evidence",), "boolean/status", "category validation and Steel services", ("ranking", "recommendation", "allocation"), "F-ELIGIBILITY", "category-specific eligibility services"),
    _calc("REC-001", "Recommendation Eligibility", "Cross-category", "deterministic status ladder", ("validation", "rules", "confidence", "scores"), "status", "modules/recommendation_eligibility.py", ("recommendation language", "human review"), "F-ELIGIBILITY", "evaluate_recommendation_eligibility"),
    _calc("ALC-001", "Standard Allocation", "Generic", "threshold and capacity constrained allocation", ("scores", "volume", "thresholds"), "% and category unit", "modules/allocation.py", ("decision", "excel", "json"), "F-ALLOC-STD", "recommend_allocation"),
    _calc("ALC-002", "Optimized Allocation", "Generic", "governed supported split selection", ("scores", "volume"), "% and category unit", "modules/allocation_optimizer.py", ("decision", "excel", "json"), "F-ALLOC-OPT", "optimize_allocation"),
    _calc("SCN-001", "Generic Procurement Scenario", "Generic", "controlled mutation then rerun", ("scenario",), "scenario result", "modules/scenario_engine.py", ("score", "allocation", "decision"), "F-SCORE-GEN", "run_intelligence_scenario"),
    _calc("SCN-002", "Flexible Laminates Governed Scenario", "Flexible Laminates", "controlled C2 scenario then rerun", ("structure", "scenario"), "scenario result", "modules/scenario_engine.py", ("score", "allocation", "decision", "exports"), "F-C2-SHOULDCOST", "run_flexible_laminate_scenarios"),
    _calc("SCN-003", "Steel Governed Scenario", "Steel", "dedicated Steel scenario output", ("steel scenario",), "scenario result", "modules/steel_scenario.py", ("decision", "allocation", "exports"), "F-SCORE-STEEL", "run_steel_scenarios"),
    _calc("EXP-001", "Excel Evidence Package", "Cross-category", "serialize authoritative tables", ("outputs",), "xlsx", "modules/exports.py", ("audit evidence",), "F-COM-VOLUME", "build_excel_workbook"),
    _calc("EXP-002", "JSON Decision Audit", "Cross-category", "strict JSON normalization", ("decision package",), "json", "modules/exports.py", ("audit evidence",), "F-COM-VOLUME", "build_decision_package_json"),
)


def _assumption(aid, name, category, key, unit, source, editable, scope, rules, default=None, source_level="category_default"):
    return AssumptionDefinition(aid, name, category, key, unit, source, editable, scope, rules, default_reference=default, source_level=source_level)


ASSUMPTIONS = (
    _assumption("COM-A01", "Annual Volume", "Cross-category", "annual_volume", "category unit", "modules/sidebar.py", True, "controlled", ("positive",), 500000),
    _assumption("COM-A02", "USD-INR FX Rate", "Cross-category", "fx_rate", "INR/USD", "modules/sidebar.py", True, "controlled", ("finite", "greater than zero"), "DEFAULT_FX_RATE", "global_default"),
    _assumption("COM-A03", "Display Currency", "Cross-category", "display_currency", "mode", "modules/sidebar.py", True, "controlled", ("USD, INR or Both",), "Both"),
    _assumption("PET-A01", "PET Resin Commodity Baseline", "PET Resin", "pet_resin_baseline", "USD/kg", "modules/raw_material_cost.py", False, "none", ("finite", "non-negative"), "COMMODITY_BASELINES['PET Resin']"),
    _assumption("KRF-A01", "Fibre Basis", "Kraft Paper", "kraft_variant", "profile", "modules/sidebar.py", True, "controlled", ("Recycled Kraft or Virgin Kraft",), "Recycled Kraft"),
    _assumption("KRF-A02", "GSM", "Kraft Paper", "kraft_gsm", "gsm", "modules/sidebar.py", True, "controlled", ("whole number", "120, 150 or 180"), 150),
    _assumption("KRF-A03", "Strength Grade", "Kraft Paper", "kraft_strength_grade", "BF", "modules/sidebar.py", True, "controlled", ("18 BF, 22 BF or 28 BF",), "22 BF"),
    _assumption("COR-A01", "Generic Packaging Components", "Corrugated Board", "packaging_should_cost_defaults", "USD/unit", "modules/should_cost.py", False, "none", ("finite", "non-negative"), "DEFAULT_PACKAGING_SHOULD_COST"),
    _assumption("LAM-A01", "Laminate Structure", "Flexible Laminates", "laminate_structure", "profile", "modules/sidebar.py", True, "controlled", ("supported governed structure",), "PET / PE"),
    _assumption("LAM-A02", "Total Micron", "Flexible Laminates", "laminate_total_micron", "micron", "modules/sidebar.py", True, "controlled", ("35 to 140",), 70),
    _assumption("LAM-A03", "Printing Loss", "Flexible Laminates", "laminate_printing_loss_pct", "%", "modules/sidebar.py", True, "controlled", ("0 to 8",), 3.0),
    _assumption("LAM-A04", "Lamination Loss", "Flexible Laminates", "laminate_lamination_loss_pct", "%", "modules/sidebar.py", True, "controlled", ("0 to 6",), 2.0),
    _assumption("LAM-A05", "Slitting Loss", "Flexible Laminates", "laminate_slitting_loss_pct", "%", "modules/sidebar.py", True, "controlled", ("0 to 5", "combined effective loss below 15%"), 1.0),
    _assumption("LAM-A06", "Tooling Cost per Colour", "Flexible Laminates", "laminate_tooling_cost_per_colour_usd", "USD/colour", "modules/sidebar.py", True, "controlled", ("non-negative",), 250.0),
    _assumption("LAM-A07", "Tooling Lifetime Volume", "Flexible Laminates", "laminate_tooling_lifetime_volume_kg", "kg", "modules/sidebar.py", True, "controlled", ("positive when applicable",), 250000.0),
    _assumption("STL-A01", "Steel Profile", "Steel", "steel_profile", "profile", "modules/steel_ux.py", True, "controlled", ("governed profile",), "CR_COIL_COMMERCIAL"),
    _assumption("STL-A02", "Sourcing Route", "Steel", "steel_sourcing_route", "route", "modules/steel_ux.py", True, "controlled", ("Domestic or Import",), "Domestic"),
    _assumption("STL-A03", "Zinc Cost", "Steel", "steel_zinc_cost_usd_per_kg", "USD/kg", "modules/steel_ux.py", True, "controlled", ("profile applicable", "non-negative"), "profile default"),
    _assumption("STL-A04", "Paint or Treatment Cost", "Steel", "steel_paint_treatment_usd_per_kg", "USD/kg", "modules/steel_ux.py", True, "controlled", ("profile applicable", "non-negative"), "profile default"),
    _assumption("STL-A05", "Import Duty", "Steel", "steel_import_duty_pct", "%", "modules/steel_ux.py", True, "controlled", ("0 to 100", "zero for Domestic"), 0.0),
    _assumption("STL-A06", "Steel Yield", "Steel", "steel_yield_pct", "%", "modules/steel_cost.py", False, "none", ("greater than zero", "no more than 100"), 96.0),
    _assumption("STL-A07", "Steel Supplier Margin", "Steel", "steel_supplier_margin_pct", "%", "modules/steel_cost.py", False, "none", ("0 to below 100",), 8.0),
    _assumption("GEN-A01", "Raw Material Shock", "Generic", "raw_material_shock", "fraction", "modules/sidebar.py", True, "scenario", ("controlled range",), 0.0, "rfq_scenario_override"),
    _assumption("GEN-A02", "Freight Shock", "Generic", "freight_shock", "fraction", "modules/sidebar.py", True, "scenario", ("controlled range",), 0.0, "rfq_scenario_override"),
    _assumption("GEN-A03", "Demand Change", "Generic", "demand_change", "fraction", "modules/sidebar.py", True, "scenario", ("controlled range",), 0.0, "rfq_scenario_override"),
    _assumption("ALC-A01", "Maximum Supplier Share", "Generic", "max_supplier_share", "%", "modules/sidebar.py", True, "controlled", ("50 to 100",), 75),
    _assumption("ALC-A02", "Minimum Backup Share", "Generic", "min_backup_share", "%", "modules/sidebar.py", True, "controlled", ("0 to 40",), 25),
    _assumption("ALC-A03", "Minimum Risk Score", "Generic", "min_risk_score", "score/100", "modules/sidebar.py", True, "controlled", ("0 to 100",), 55),
    _assumption("ALC-A04", "Minimum ESG Score", "Generic", "min_esg_score", "score/100", "modules/sidebar.py", True, "controlled", ("0 to 100",), 50),
)

EXCEL_EVIDENCE_MAP = {
    "SCR-001": "Supplier Scores Report; Audit Supplier Scores", "SCR-002": "Supplier Comparison; Audit Supplier Scores",
    "PET-001": "Should Cost", "KRF-001": "Should Cost", "COR-001": "Should Cost", "LAM-004": "Should Cost; C2 Governance", "STL-003": "Steel Should Cost",
    "ALC-001": "Allocation; Standard Allocation", "ALC-002": "Optimized Allocation", "SCN-001": "Scenarios", "SCN-002": "Scenarios; C2 Governance", "SCN-003": "Steel Scenarios",
}
JSON_EVIDENCE_MAP = {
    "SCR-001": "recommended_supplier; value_metrics", "SCR-002": "steel_governance.recommendation", "ALC-001": "allocation", "ALC-002": "optimized_allocation",
    "SCN-001": "scenarios", "SCN-002": "flexible_laminates_governance.scenarios", "SCN-003": "steel_governance.scenarios",
}


def calculation_by_id(calculation_id: str) -> CalculationDefinition:
    return next(item for item in CALCULATIONS if item.calculation_id == calculation_id)


def assumption_by_key(key: str) -> AssumptionDefinition | None:
    return next((item for item in ASSUMPTIONS if item.key == key), None)
