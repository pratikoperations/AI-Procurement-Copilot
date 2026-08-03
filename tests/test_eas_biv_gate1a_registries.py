"""Gate 1A registry, provenance and metadata-accuracy contracts."""
from dataclasses import asdict
import importlib

from modules.assumption_provenance import classify_assumption
from modules.calculation_catalogue import (
    ASSUMPTIONS,
    CALCULATIONS,
    FORMULAS,
    HUMAN_REVIEW_BOUNDARY,
    STRATEGIC_FIT_STATUS,
    UNDOCUMENTED_DEFAULT,
)
from modules.export_evidence_registry import EXPORT_EVIDENCE, STEEL_EXCEL_LOCATIONS
from modules.governance_rule_registry import DEFERRED_RULES, RULES
from modules.parameter_profile_records import EVIDENCE_CLASSIFICATIONS, ParameterProfileRecord
from modules.steel_exports import STEEL_EXCEL_SHEETS
from modules.weight_profile_registry import WEIGHT_PROFILES, validate_weight_profiles


def test_all_registry_ids_are_unique():
    groups = [
        [x.formula_id for x in FORMULAS],
        [x.calculation_id for x in CALCULATIONS],
        [x.assumption_id for x in ASSUMPTIONS],
        [x.profile_id for x in WEIGHT_PROFILES],
        [x.rule_id for x in RULES],
        [x.evidence_id for x in EXPORT_EVIDENCE],
    ]
    for ids in groups:
        assert len(ids) == len(set(ids))


def _assert_exact_or_umbrella_source(source_file: str, source_function: str):
    if source_function.startswith("umbrella:"):
        assert source_file.startswith("umbrella:") or ";" in source_file
        assert len([part for part in source_function.removeprefix("umbrella:").split(";") if part.strip()]) >= 2
        return
    module_name = source_file.removesuffix(".py").replace("/", ".")
    module = importlib.import_module(module_name)
    assert hasattr(module, source_function), f"{source_file}:{source_function} does not exist"


def test_formula_contract_is_complete_non_executable_and_sources_resolve():
    for formula in FORMULAS:
        assert formula.version and formula.source_file and formula.source_function
        assert formula.input_definitions and formula.input_units
        assert formula.output_definition and formula.output_unit
        assert formula.status == "active"
        assert "eval(" not in formula.expression.lower()
        _assert_exact_or_umbrella_source(formula.source_file, formula.source_function)


def test_required_category_and_domain_coverage():
    categories = {x.category for x in CALCULATIONS}
    assert {"PET Resin", "Kraft Paper", "Corrugated Board", "Flexible Laminates", "Steel"} <= categories
    ids = {x.calculation_id for x in CALCULATIONS}
    assert {
        "TCO-001", "TCO-002", "PER-001", "PER-002", "PER-003", "PER-004",
        "PER-005", "PER-006", "ESG-001", "ELG-001", "REC-001", "ALC-001",
        "ALC-002", "SCN-001", "SCN-002", "SCN-003", "EXP-001", "EXP-002",
    } <= ids


def test_calculations_reference_versioned_formulas_and_exact_or_umbrella_sources():
    formula_ids = {x.formula_id for x in FORMULAS}
    for calc in CALCULATIONS:
        assert calc.formula_id in formula_ids
        assert calc.formula_version and calc.source_module and calc.source_function and calc.unit
        _assert_exact_or_umbrella_source(calc.source_module, calc.source_function)


def test_scenario_source_functions_and_formula_families_are_exact():
    by_id = {x.calculation_id: x for x in CALCULATIONS}
    assert by_id["SCN-001"].source_function == "run_intelligence_scenario"
    assert by_id["SCN-002"].source_function == "run_all_flexible_laminate_scenarios"
    assert by_id["SCN-003"].source_function == "run_governed_steel_scenarios"
    assert by_id["SCN-001"].formula_id == "F-SCENARIO-GENERIC"
    assert by_id["SCN-002"].formula_id == "F-SCENARIO-C2"
    assert by_id["SCN-003"].formula_id == "F-SCENARIO-STEEL"
    assert "run_flexible_laminate_scenarios" not in {x.source_function for x in CALCULATIONS}
    assert "run_steel_scenarios" not in {x.source_function for x in CALCULATIONS}


def test_performance_and_esg_metadata_match_authoritative_weights():
    formulas = {x.formula_id: x for x in FORMULAS}
    performance = formulas["F-PERFORMANCE"]
    esg = formulas["F-ESG"]
    assert "0.32" in performance.expression
    assert performance.expression.count("0.23") == 2
    assert "0.12" in performance.expression and "0.10" in performance.expression
    assert "0.30" in esg.expression and "0.25" in esg.expression
    assert esg.expression.count("0.20") == 2
    assert "0.05" in esg.expression
    assert {x.formula_id for x in CALCULATIONS if x.calculation_id.startswith("PER-")} == {"F-PERFORMANCE"}
    assert next(x for x in CALCULATIONS if x.calculation_id == "ESG-001").formula_id == "F-ESG"


def test_assumption_contract_discloses_unknown_provenance():
    for item in ASSUMPTIONS:
        assert item.version and item.unit and item.source_module
        assert item.evidence_classification in EVIDENCE_CLASSIFICATIONS
        if item.evidence_classification == UNDOCUMENTED_DEFAULT:
            assert item.source_reference is None
            assert item.approver is None
            assert item.confidence is None
            assert item.effective_date is None


def test_uncatalogued_value_does_not_fabricate_evidence():
    result = classify_assumption("unknown_parameter", 12.5)
    assert result["value"] == 12.5
    assert result["evidence_classification"] == UNDOCUMENTED_DEFAULT
    assert result["source_reference"] is None
    assert result["approver"] is None
    assert result["confidence"] is None


def test_supported_evidence_classifications_are_complete():
    required = {
        "uploaded fact", "manually entered fact", "supplier-declared value",
        "historical measured value", "external benchmark", "system-derived value",
        "predicted value", "approved assumption", "default assumption",
        "existing undocumented controlled default",
    }
    assert required <= set(EVIDENCE_CLASSIFICATIONS)


def test_weight_profiles_reconcile_and_steel_remains_dedicated():
    validate_weight_profiles()
    steel = next(x for x in WEIGHT_PROFILES if x.profile_id == "WGT-STL-001")
    assert steel.weights == {}
    assert "Dedicated governed Steel" in steel.governance_notes


def test_blocks_are_not_weighted_contributions_and_unverified_deviation_is_deferred():
    weighted = next(x for x in RULES if x.rule_type == "weighted_contribution")
    technical = next(x for x in RULES if x.rule_type == "technical_ineligibility")
    assert not weighted.blocking
    assert technical.blocking
    assert all(x.human_approval_required for x in RULES)
    assert any(x.rule_type == "recommendation_withholding" for x in RULES)
    assert not any(x.rule_type == "approved_deviation" for x in RULES)
    assert "approved_deviation" in DEFERRED_RULES


def test_export_evidence_records_only_the_authorized_c2_schema_migration():
    migration_ids = {item.evidence_id for item in EXPORT_EVIDENCE if item.schema_change}
    assert migration_ids == {"EXP-EV-004", "EXP-EV-006"}
    for item in EXPORT_EVIDENCE:
        assert item.calculation_ids and item.location and item.source_function
    assert tuple(STEEL_EXCEL_SHEETS) == STEEL_EXCEL_LOCATIONS
    all_locations = "; ".join(item.location for item in EXPORT_EVIDENCE)
    assert "Steel Should Cost" not in all_locations
    assert "Steel Scenarios" not in all_locations
    all_functions = "; ".join(item.source_function for item in EXPORT_EVIDENCE)
    assert "build_steel_decision_package_json" not in all_functions
    assert "build_steel_governance_manifest" in all_functions
    assert "build_steel_json_export" in all_functions


def test_registered_json_paths_match_canonical_c2_and_existing_steel_contracts():
    c2 = next(x for x in EXPORT_EVIDENCE if x.evidence_id == "EXP-EV-006")
    steel = next(x for x in EXPORT_EVIDENCE if x.evidence_id == "EXP-EV-007")
    c2_paths = {path.strip() for path in c2.location.split(";")}
    assert {
        "canonical_allocation",
        "scenario_allocations",
        "flexible_laminates_governance.export_contract_version",
        "flexible_laminates_governance.canonical_allocation",
        "flexible_laminates_governance.scenario_allocations",
        "flexible_laminates_governance.human_review_required",
        "flexible_laminates_governance.legacy_fallback_used",
    } <= c2_paths
    assert "optimized_allocation" not in c2_paths
    assert "flexible_laminates_governance.optimized_allocation" not in c2_paths
    assert "flexible_laminates_governance.standard_allocation" not in c2_paths
    for path in (
        "steel_governance.winner",
        "steel_governance.winner_state",
        "steel_governance.human_approval_required",
        "steel_governance.scenarios",
    ):
        assert path in steel.location
    assert "steel_governance.recommendation" not in steel.location
    assert steel.schema_change is False


def test_scenario_and_export_records_use_dedicated_formula_references():
    by_id = {x.calculation_id: x for x in CALCULATIONS}
    assert by_id["EXP-001"].formula_id == "F-EXPORT-EXCEL"
    assert by_id["EXP-002"].formula_id == "F-EXPORT-JSON"
    assert all(not by_id[cid].formula_id.startswith("F-SCORE") for cid in ("SCN-001", "SCN-002", "SCN-003"))


def test_strategic_fit_and_effective_dates_remain_transparent():
    assert STRATEGIC_FIT_STATUS.startswith("deferred")
    assert all(item.effective_date is None for item in ASSUMPTIONS if item.evidence_classification == UNDOCUMENTED_DEFAULT)


def test_parameter_profile_contract_validates_source_and_evidence():
    record = ParameterProfileRecord("PAR-001", "COM-A01", 1000, "kg", "kg", "Kraft Paper", None, None, "category_default", UNDOCUMENTED_DEFAULT)
    assert asdict(record)["confidence"] is None


def test_human_review_boundary_is_explicit():
    assert "Human approval is mandatory" in HUMAN_REVIEW_BOUNDARY
