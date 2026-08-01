"""Versioned read-only metadata for calculation explainability.

Expressions are documentation only. Existing procurement engines remain the
sole authoritative source of business results.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Tuple

HUMAN_REVIEW_BOUNDARY = (
    "Controlled portfolio decision support only. Human approval is mandatory. "
    "No autonomous award, production allocation, engineering certification, "
    "live-market claim or realized-savings claim is permitted."
)
UNDOCUMENTED_DEFAULT = "existing undocumented controlled default"

@dataclass(frozen=True)
class FormulaDefinition:
    formula_id: str; version: str; business_name: str; description: str
    category_applicability: Tuple[str, ...]; source_file: str; source_function: str
    input_definitions: Tuple[str, ...]; input_units: Tuple[str, ...]
    expression: str; intermediate_steps: Tuple[str, ...]
    output_definition: str; output_unit: str
    owner: str = "Procurement decision-support owner"; status: str = "active"
    effective_date: str | None = None; governance_notes: str = HUMAN_REVIEW_BOUNDARY

@dataclass(frozen=True)
class CalculationDefinition:
    calculation_id: str; business_name: str; category: str; formula_text: str
    variables: Tuple[str, ...]; unit: str; source_module: str
    downstream_outputs: Tuple[str, ...]; formula_id: str
    formula_version: str = "1.0"; description: str = "Authoritative deterministic application result."
    source_function: str = ""; owner: str = "Procurement decision-support owner"
    status: str = "active"; effective_date: str | None = None
    governance_caveat: str = HUMAN_REVIEW_BOUNDARY

@dataclass(frozen=True)
class AssumptionDefinition:
    assumption_id: str; business_name: str; category: str; key: str; unit: str
    source_module: str; editable: bool; edit_scope: str
    validation_rules: Tuple[str, ...]; default_reference: Any = None
    original_unit: str | None = None; supplier_scope: str | None = None
    rfq_scenario_scope: str | None = None; source_level: str = "category_default"
    evidence_classification: str = UNDOCUMENTED_DEFAULT
    source_reference: str | None = None; effective_date: str | None = None
    review_expiry_date: str | None = None; confidence: float | None = None
    override_status: str = "not_overridden"; override_reason: str | None = None
    approver: str | None = None; version: str = "1.0"
    governance_caveat: str = HUMAN_REVIEW_BOUNDARY


def _formula(fid, name, cats, file, func, expr, inputs, units, steps, output, outunit):
    return FormulaDefinition(fid, "1.0", name, name, cats, file, func, inputs, units, expr, steps, output, outunit)

FORMULAS = (
    _formula("F-COM-VOLUME", "Effective annual volume", ("All",), "modules/category_cost_router.py", "calculate_category_should_cost", "annual_volume * (1 + demand_change)", ("annual_volume", "demand_change"), ("category unit", "fraction"), ("resolve volume", "apply demand"), "effective volume", "category unit"),
    _formula("F-COM-FX", "USD-INR conversion", ("All",), "modules/steel_cost.py", "steel_should_cost_dataframe", "usd_value * fx_rate", ("usd_value", "fx_rate"), ("USD", "INR/USD"), ("read FX", "convert"), "INR value", "INR"),
    _formula("F-RM-SHOULDCOST", "Raw-material should-cost", ("PET Resin", "Kraft Paper", "Raw materials"), "modules/raw_material_cost.py", "calculate_raw_material_should_cost", "sum(adjusted components)", ("baseline", "shocks"), ("USD/kg", "fraction"), ("resolve baseline", "apply shocks", "sum"), "target cost", "USD/kg"),
    _formula("F-PKG-SHOULDCOST", "Generic packaging should-cost", ("Corrugated Board", "Generic packaging"), "modules/should_cost.py", "calculate_packaging_should_cost", "sum(adjusted components) * (1 + fx_shock)", ("components", "shocks"), ("USD/unit", "fraction"), ("adjust", "sum"), "target cost", "USD/unit"),
    _formula("F-C2-SHOULDCOST", "Flexible Laminates should-cost", ("Flexible Laminates",), "modules/flexible_laminate_cost.py", "calculate_flexible_laminate_should_cost", "authoritative C2 component reconciliation", ("structure", "losses", "tooling", "shocks"), ("mixed", "%", "USD/kg", "fraction"), ("substrate", "conversion", "yield", "tooling", "freight", "margin"), "target cost", "USD/kg"),
    _formula("F-C3-SHOULDCOST", "Steel should-cost", ("Steel",), "modules/steel_cost.py", "calculate_steel_should_cost", "authoritative Steel component reconciliation", ("components", "yield", "route", "duty", "margin"), ("USD/kg", "%", "route", "%", "%"), ("recurring net", "yield", "landed", "duty", "margin"), "target cost", "USD/kg"),
    _formula("F-TCO-PKG", "Packaging risk-adjusted TCO", ("Packaging",), "modules/tco.py", "calculate_supplier_tco", "scenario price + freight + inventory + working capital + risk + lead buffer", ("supplier row", "volume", "scenario"), ("mixed", "category unit", "mixed"), ("price", "freight", "inventory", "capital", "risk", "lead"), "adjusted TCO", "USD/unit"),
    _formula("F-TCO-RM", "Raw-material TCO", ("Raw materials",), "modules/raw_material_tco.py", "calculate_raw_material_tco", "authoritative raw-material TCO service", ("supplier row", "volume", "scenario"), ("mixed", "kg", "mixed"), ("resolve inputs", "run service"), "adjusted TCO", "USD/kg"),
    _formula("F-RISK-GEN", "Generic risk resilience", ("Generic",), "modules/risk.py", "calculate_risk", "normalize(100 - sum(risk penalties))", ("payment", "incoterm", "lead", "MOQ", "OTIF", "PPM"), ("terms", "term", "days", "unit", "%", "PPM"), ("penalties", "sum", "normalize", "band"), "risk score", "score/100"),
    _formula("F-SCORE-GEN", "Generic weighted supplier score", ("Packaging", "Raw materials"), "modules/scoring.py", "enrich_supplier_scores", "sum(factor score * weight)", ("factor scores", "weights"), ("score/100", "fraction"), ("normalize", "weight", "round"), "total score", "score/100"),
    _formula("F-SCORE-STEEL", "Governed Steel supplier score", ("Steel",), "modules/steel_risk.py", "score_and_recommend_steel_suppliers", "authoritative governed Steel score", ("evidence", "profile", "substitution"), ("mixed", "profile", "state"), ("eligibility", "risk", "score"), "governed score", "score/100"),
    _formula("F-ALLOC-STD", "Standard allocation", ("Generic",), "modules/allocation.py", "recommend_allocation", "authoritative allocation rules", ("scores", "volume", "thresholds"), ("table", "category unit", "mixed"), ("eligibility", "thresholds", "capacity", "concentration"), "allocation", "% and category unit"),
    _formula("F-ALLOC-OPT", "Optimized allocation", ("Generic",), "modules/allocation_optimizer.py", "optimize_allocation", "authoritative supported split selection", ("scores", "volume"), ("table", "category unit"), ("eligible suppliers", "candidate splits", "selection"), "optimized allocation", "% and category unit"),
    _formula("F-ELIGIBILITY", "Recommendation eligibility", ("All",), "modules/recommendation_eligibility.py", "evaluate_recommendation_eligibility", "deterministic status ladder", ("validation", "rules", "confidence", "scores", "volume"), ("records", "records", "score/100", "table", "category unit"), ("blockers", "confidence", "conditions", "language"), "eligibility", "status"),
)


def _calc(cid, name, category, formula, variables, unit, source, outputs, fid, function, note=HUMAN_REVIEW_BOUNDARY):
    return CalculationDefinition(cid, name, category, formula, variables, unit, source, outputs, fid, source_function=function, governance_caveat=note)

CALCULATIONS = (
    _calc("COM-001", "Effective Annual Volume", "Cross-category", "annual_volume * (1 + demand_change)", ("annual_volume", "demand_change"), "category unit", "modules/category_cost_router.py", ("should_cost", "tco", "allocation", "exports"), "F-COM-VOLUME", "calculate_category_should_cost"),
    _calc("COM-002", "USD to INR Conversion", "Cross-category", "usd_value * fx_rate", ("usd_value", "fx_rate"), "INR", "modules/steel_cost.py", ("display", "excel", "json"), "F-COM-FX", "steel_should_cost_dataframe"),
    _calc("COM-003", "Annual Value", "Cross-category", "unit_value * annual_volume", ("unit_value", "annual_volume"), "currency/year", "category dataframe/export services", ("dashboard", "excel", "json"), "F-COM-VOLUME", "category dataframe services"),
    _calc("PET-001", "PET Resin Target Unit Cost", "PET Resin", "sum(adjusted components)", ("baseline", "shocks"), "USD/kg", "modules/raw_material_cost.py", ("should_cost", "recommendation", "exports"), "F-RM-SHOULDCOST", "calculate_raw_material_should_cost"),
    _calc("KRF-001", "Kraft Paper Target Unit Cost", "Kraft Paper", "sum(adjusted governed components)", ("variant", "gsm", "strength", "shocks"), "USD/kg", "modules/raw_material_cost.py", ("should_cost", "recommendation", "exports"), "F-RM-SHOULDCOST", "calculate_raw_material_should_cost", "GSM premium represents controlled profile availability, not physical mass consumption."),
    _calc("COR-001", "Corrugated Board Target Unit Cost", "Corrugated Board", "sum(adjusted generic packaging components)", ("components", "shocks"), "USD/unit", "modules/should_cost.py", ("should_cost", "recommendation", "exports"), "F-PKG-SHOULDCOST", "calculate_packaging_should_cost"),
    _calc("LAM-001", "Flexible Laminates Substrate Cost", "Flexible Laminates", "sum(material share * price * shock)", ("structure", "shock"), "USD/kg", "modules/flexible_laminate_cost.py", ("should_cost", "scenario", "exports"), "F-C2-SHOULDCOST", "calculate_flexible_laminate_should_cost", "Total micron is metadata only; fixed synthetic mass-share profiles are authoritative."),
    _calc("LAM-002", "Flexible Laminates Compounded Yield", "Flexible Laminates", "(1-print loss)*(1-lamination loss)*(1-slitting loss)", ("losses",), "factor", "modules/flexible_laminate_cost.py", ("process_loss", "target_cost"), "F-C2-SHOULDCOST", "calculate_flexible_laminate_should_cost"),
    _calc("LAM-003", "Flexible Laminates Tooling Amortisation", "Flexible Laminates", "colours * cost / lifetime volume", ("colours", "cost", "volume", "status"), "USD/kg", "modules/flexible_laminate_cost.py", ("should_cost", "scenario", "exports"), "F-C2-SHOULDCOST", "calculate_flexible_laminate_should_cost"),
    _calc("LAM-004", "Flexible Laminates Target Unit Cost", "Flexible Laminates", "authoritative C2 component sum", ("components",), "USD/kg", "modules/flexible_laminate_cost.py", ("recommendation", "scenario", "exports"), "F-C2-SHOULDCOST", "calculate_flexible_laminate_should_cost"),
    _calc("STL-001", "Steel Recurring Gross Cost", "Steel", "recurring_net / yield", ("components", "yield"), "USD/kg", "modules/steel_cost.py", ("yield_loss", "landed"), "F-C3-SHOULDCOST", "calculate_steel_should_cost"),
    _calc("STL-002", "Steel Import Duty", "Steel", "landed_pre_duty * duty when Import", ("route", "duty"), "USD/kg", "modules/steel_cost.py", ("target_cost", "exports"), "F-C3-SHOULDCOST", "calculate_steel_should_cost"),
    _calc("STL-003", "Steel Target Unit Cost", "Steel", "landed + duty + margin", ("components", "yield", "route", "margin"), "USD/kg", "modules/steel_cost.py", ("score", "scenario", "allocation", "exports"), "F-C3-SHOULDCOST", "calculate_steel_should_cost"),
    _calc("TCO-001", "Packaging Risk-Adjusted TCO", "Generic Packaging", "authoritative packaging TCO", ("supplier", "volume", "scenario"), "USD/unit", "modules/tco.py", ("score", "recommendation", "allocation", "exports"), "F-TCO-PKG", "calculate_supplier_tco"),
    _calc("TCO-002", "Raw-Material Risk-Adjusted TCO", "Raw Material", "authoritative raw-material TCO", ("supplier", "volume", "scenario"), "USD/kg", "modules/raw_material_tco.py", ("score", "recommendation", "allocation", "exports"), "F-TCO-RM", "calculate_raw_material_tco"),
    _calc("RSK-001", "Supplier Risk Resilience", "Generic", "normalize(100 - penalties)", ("risk inputs",), "score/100", "modules/risk.py", ("tco", "score", "allocation"), "F-RISK-GEN", "calculate_risk"),
    _calc("SCR-001", "Generic Weighted Supplier Score", "Generic", "sum(normalized factor * weight)", ("factors", "weights"), "score/100", "modules/scoring.py", ("ranking", "recommendation", "allocation"), "F-SCORE-GEN", "enrich_supplier_scores"),
    _calc("SCR-002", "Governed Steel Supplier Score", "Steel", "authoritative governed Steel score", ("evidence", "profile", "substitution"), "score/100", "modules/steel_risk.py", ("recommendation", "allocation", "scenario"), "F-SCORE-STEEL", "score_and_recommend_steel_suppliers"),
    _calc("PER-001", "Quality and Performance Score", "Generic", "authoritative performance service", ("quality and service",), "score/100", "modules/performance.py", ("weighted score", "recommendation"), "F-SCORE-GEN", "calculate_performance_score"),
    _calc("ESG-001", "ESG Score", "Generic", "authoritative ESG service", ("ESG fields",), "score/100", "modules/esg.py", ("weighted score", "allocation"), "F-SCORE-GEN", "calculate_esg_score"),
    _calc("ELG-001", "Technical Eligibility", "Cross-category", "authoritative category eligibility", ("technical evidence",), "boolean/status", "category validation and Steel services", ("ranking", "recommendation", "allocation"), "F-ELIGIBILITY", "category-specific eligibility services"),
    _calc("REC-001", "Recommendation Eligibility", "Cross-category", "deterministic status ladder", ("validation", "rules", "confidence", "scores"), "status", "modules/recommendation_eligibility.py", ("recommendation language", "human review"), "F-ELIGIBILITY", "evaluate_recommendation_eligibility"),
    _calc("ALC-001", "Standard Allocation", "Generic", "threshold and capacity constrained allocation", ("scores", "volume", "thresholds"), "% and category unit", "modules/allocation.py", ("decision", "excel", "json"), "F-ALLOC-STD", "recommend_allocation"),
    _calc("ALC-002", "Optimized Allocation", "Generic", "governed supported split selection", ("scores", "volume"), "% and category unit", "modules/allocation_optimizer.py", ("decision", "excel", "json"), "F-ALLOC-OPT", "optimize_allocation"),
    _calc("SCN-001", "Generic Procurement Scenario", "Generic", "controlled mutation then rerun", ("scenario",), "scenario result", "modules/scenario_engine.py", ("score", "allocation", "decision"), "F-SCORE-GEN", "run_intelligence_scenario"),
    _calc("SCN-002", "Flexible Laminates Governed Scenario", "Flexible Laminates", "controlled C2 scenario then rerun", ("structure", "scenario"), "scenario result", "modules/scenario_engine.py", ("score", "allocation", "decision", "exports"), "F-C2-SHOULDCOST", "run_flexible_laminate_scenarios"),
    _calc("SCN-003", "Steel Governed Scenario", "Steel", "dedicated Steel scenario output", ("scenario",), "scenario result", "modules/steel_scenario.py", ("decision", "allocation", "exports"), "F-SCORE-STEEL", "run_steel_scenarios"),
    _calc("EXP-001", "Excel Evidence Package", "Cross-category", "serialize authoritative tables", ("outputs",), "xlsx", "modules/exports.py", ("audit evidence",), "F-COM-VOLUME", "build_excel_workbook"),
    _calc("EXP-002", "JSON Decision Audit", "Cross-category", "strict JSON normalization", ("decision package",), "json", "modules/exports.py", ("audit evidence",), "F-COM-VOLUME", "build_decision_package_json"),
)


def _assume(aid, name, category, key, unit, source, editable, scope, rules, default=None, level="category_default"):
    return AssumptionDefinition(aid, name, category, key, unit, source, editable, scope, rules, default_reference=default, source_level=level)

ASSUMPTIONS = (
    _assume("COM-A01", "Annual Volume", "Cross-category", "annual_volume", "category unit", "modules/sidebar.py", True, "controlled", ("positive",), 500000),
    _assume("COM-A02", "USD-INR FX Rate", "Cross-category", "fx_rate", "INR/USD", "modules/sidebar.py", True, "controlled", ("finite", "greater than zero"), "DEFAULT_FX_RATE", "global_default"),
    _assume("COM-A03", "Display Currency", "Cross-category", "display_currency", "mode", "modules/sidebar.py", True, "controlled", ("USD, INR or Both",), "Both"),
    _assume("PET-A01", "PET Resin Commodity Baseline", "PET Resin", "pet_resin_baseline", "USD/kg", "modules/raw_material_cost.py", False, "none", ("finite", "non-negative"), "COMMODITY_BASELINES['PET Resin']"),
    _assume("KRF-A01", "Fibre Basis", "Kraft Paper", "kraft_variant", "profile", "modules/sidebar.py", True, "controlled", ("supported profile",), "Recycled Kraft"),
    _assume("KRF-A02", "GSM", "Kraft Paper", "kraft_gsm", "gsm", "modules/sidebar.py", True, "controlled", ("120, 150 or 180",), 150),
    _assume("KRF-A03", "Strength Grade", "Kraft Paper", "kraft_strength_grade", "BF", "modules/sidebar.py", True, "controlled", ("18, 22 or 28 BF",), "22 BF"),
    _assume("COR-A01", "Generic Packaging Components", "Corrugated Board", "packaging_should_cost_defaults", "USD/unit", "modules/should_cost.py", False, "none", ("finite", "non-negative"), "DEFAULT_PACKAGING_SHOULD_COST"),
    _assume("LAM-A01", "Laminate Structure", "Flexible Laminates", "laminate_structure", "profile", "modules/sidebar.py", True, "controlled", ("supported structure",), "PET / PE"),
    _assume("LAM-A02", "Total Micron", "Flexible Laminates", "laminate_total_micron", "micron", "modules/sidebar.py", True, "controlled", ("35 to 140",), 70),
    _assume("LAM-A03", "Printing Loss", "Flexible Laminates", "laminate_printing_loss_pct", "%", "modules/sidebar.py", True, "controlled", ("0 to 8",), 3.0),
    _assume("LAM-A04", "Lamination Loss", "Flexible Laminates", "laminate_lamination_loss_pct", "%", "modules/sidebar.py", True, "controlled", ("0 to 6",), 2.0),
    _assume("LAM-A05", "Slitting Loss", "Flexible Laminates", "laminate_slitting_loss_pct", "%", "modules/sidebar.py", True, "controlled", ("0 to 5", "combined below 15"), 1.0),
    _assume("LAM-A06", "Tooling Cost per Colour", "Flexible Laminates", "laminate_tooling_cost_per_colour_usd", "USD/colour", "modules/sidebar.py", True, "controlled", ("non-negative",), 250.0),
    _assume("LAM-A07", "Tooling Lifetime Volume", "Flexible Laminates", "laminate_tooling_lifetime_volume_kg", "kg", "modules/sidebar.py", True, "controlled", ("positive when applicable",), 250000.0),
    _assume("STL-A01", "Steel Profile", "Steel", "steel_profile", "profile", "modules/steel_ux.py", True, "controlled", ("governed profile",), "CR_COIL_COMMERCIAL"),
    _assume("STL-A02", "Sourcing Route", "Steel", "steel_sourcing_route", "route", "modules/steel_ux.py", True, "controlled", ("Domestic or Import",), "Domestic"),
    _assume("STL-A03", "Zinc Cost", "Steel", "steel_zinc_cost_usd_per_kg", "USD/kg", "modules/steel_ux.py", True, "controlled", ("profile applicable", "non-negative"), "profile default"),
    _assume("STL-A04", "Paint or Treatment Cost", "Steel", "steel_paint_treatment_usd_per_kg", "USD/kg", "modules/steel_ux.py", True, "controlled", ("profile applicable", "non-negative"), "profile default"),
    _assume("STL-A05", "Import Duty", "Steel", "steel_import_duty_pct", "%", "modules/steel_ux.py", True, "controlled", ("0 to 100", "zero for Domestic"), 0.0),
    _assume("STL-A06", "Steel Yield", "Steel", "steel_yield_pct", "%", "modules/steel_cost.py", False, "none", ("greater than zero", "no more than 100"), 96.0),
    _assume("STL-A07", "Steel Supplier Margin", "Steel", "steel_supplier_margin_pct", "%", "modules/steel_cost.py", False, "none", ("0 to below 100",), 8.0),
    _assume("GEN-A01", "Raw Material Shock", "Generic", "raw_material_shock", "fraction", "modules/sidebar.py", True, "scenario", ("controlled range",), 0.0, "rfq_scenario_override"),
    _assume("GEN-A02", "Freight Shock", "Generic", "freight_shock", "fraction", "modules/sidebar.py", True, "scenario", ("controlled range",), 0.0, "rfq_scenario_override"),
    _assume("GEN-A03", "Demand Change", "Generic", "demand_change", "fraction", "modules/sidebar.py", True, "scenario", ("controlled range",), 0.0, "rfq_scenario_override"),
    _assume("ALC-A01", "Maximum Supplier Share", "Generic", "max_supplier_share", "%", "modules/sidebar.py", True, "controlled", ("50 to 100",), 75),
    _assume("ALC-A02", "Minimum Backup Share", "Generic", "min_backup_share", "%", "modules/sidebar.py", True, "controlled", ("0 to 40",), 25),
    _assume("ALC-A03", "Minimum Risk Score", "Generic", "min_risk_score", "score/100", "modules/sidebar.py", True, "controlled", ("0 to 100",), 55),
    _assume("ALC-A04", "Minimum ESG Score", "Generic", "min_esg_score", "score/100", "modules/sidebar.py", True, "controlled", ("0 to 100",), 50),
)

EXCEL_EVIDENCE_MAP = {"SCR-001":"Supplier Scores Report; Audit Supplier Scores","SCR-002":"Supplier Comparison; Audit Supplier Scores","PET-001":"Should Cost","KRF-001":"Should Cost","COR-001":"Should Cost","LAM-004":"Should Cost; C2 Governance","STL-003":"Steel Should Cost","ALC-001":"Allocation; Standard Allocation","ALC-002":"Optimized Allocation","SCN-001":"Scenarios","SCN-002":"Scenarios; C2 Governance","SCN-003":"Steel Scenarios"}
JSON_EVIDENCE_MAP = {"SCR-001":"recommended_supplier; value_metrics","SCR-002":"steel_governance.recommendation","ALC-001":"allocation","ALC-002":"optimized_allocation","SCN-001":"scenarios","SCN-002":"flexible_laminates_governance.scenarios","SCN-003":"steel_governance.scenarios"}

def calculation_by_id(calculation_id: str) -> CalculationDefinition:
    return next(item for item in CALCULATIONS if item.calculation_id == calculation_id)

def assumption_by_key(key: str) -> AssumptionDefinition | None:
    return next((item for item in ASSUMPTIONS if item.key == key), None)
