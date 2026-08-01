"""Gate 1A registry, provenance and compatibility contracts."""
from dataclasses import asdict

from modules.assumption_provenance import classify_assumption
from modules.calculation_catalogue import ASSUMPTIONS, CALCULATIONS, FORMULAS, HUMAN_REVIEW_BOUNDARY, UNDOCUMENTED_DEFAULT
from modules.export_evidence_registry import EXPORT_EVIDENCE
from modules.governance_rule_registry import RULES
from modules.parameter_profile_records import EVIDENCE_CLASSIFICATIONS, ParameterProfileRecord
from modules.weight_profile_registry import WEIGHT_PROFILES, validate_weight_profiles


def test_all_registry_ids_are_unique():
    groups = [
        [x.formula_id for x in FORMULAS], [x.calculation_id for x in CALCULATIONS],
        [x.assumption_id for x in ASSUMPTIONS], [x.profile_id for x in WEIGHT_PROFILES],
        [x.rule_id for x in RULES], [x.evidence_id for x in EXPORT_EVIDENCE],
    ]
    for ids in groups:
        assert len(ids) == len(set(ids))


def test_formula_contract_is_complete_and_non_executable():
    for formula in FORMULAS:
        assert formula.version and formula.source_file and formula.source_function
        assert formula.input_definitions and formula.input_units
        assert formula.output_definition and formula.output_unit
        assert formula.status == "active"
        assert "eval" not in formula.expression.lower()


def test_required_category_and_domain_coverage():
    names = {(x.category, x.business_name) for x in CALCULATIONS}
    assert any(c == "PET Resin" for c, _ in names)
    assert any(c == "Kraft Paper" for c, _ in names)
    assert any(c == "Corrugated Board" for c, _ in names)
    assert any(c == "Flexible Laminates" for c, _ in names)
    assert any(c == "Steel" for c, _ in names)
    ids = {x.calculation_id for x in CALCULATIONS}
    assert {"TCO-001", "TCO-002", "PER-001", "ESG-001", "ELG-001", "REC-001", "ALC-001", "ALC-002", "SCN-001", "SCN-002", "SCN-003"} <= ids


def test_calculations_reference_versioned_formulas_and_exact_sources():
    formula_ids = {x.formula_id for x in FORMULAS}
    for calc in CALCULATIONS:
        assert calc.formula_id in formula_ids
        assert calc.formula_version
        assert calc.source_module and calc.source_function
        assert calc.unit


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
    required = {"uploaded fact", "manually entered fact", "supplier-declared value", "historical measured value", "external benchmark", "system-derived value", "predicted value", "approved assumption", "default assumption", "existing undocumented controlled default"}
    assert required <= set(EVIDENCE_CLASSIFICATIONS)


def test_weight_profiles_reconcile_and_steel_remains_dedicated():
    validate_weight_profiles()
    steel = next(x for x in WEIGHT_PROFILES if x.profile_id == "WGT-STL-001")
    assert steel.weights == {}
    assert "Dedicated governed Steel" in steel.governance_notes


def test_blocks_are_not_weighted_contributions_and_human_approval_is_mandatory():
    weighted = next(x for x in RULES if x.rule_type == "weighted_contribution")
    technical = next(x for x in RULES if x.rule_type == "technical_ineligibility")
    assert not weighted.blocking
    assert technical.blocking
    assert all(x.human_approval_required for x in RULES)
    assert any(x.rule_type == "recommendation_withholding" for x in RULES)


def test_export_evidence_is_mapping_only_and_preserves_schema():
    assert EXPORT_EVIDENCE
    for item in EXPORT_EVIDENCE:
        assert item.calculation_ids and item.location and item.source_function
        assert item.schema_change is False


def test_parameter_profile_contract_validates_source_and_evidence():
    record = ParameterProfileRecord("PAR-001", "COM-A01", 1000, "kg", "kg", "Kraft Paper", None, None, "category_default", UNDOCUMENTED_DEFAULT)
    assert asdict(record)["confidence"] is None


def test_human_review_boundary_is_explicit():
    assert "Human approval is mandatory" in HUMAN_REVIEW_BOUNDARY
