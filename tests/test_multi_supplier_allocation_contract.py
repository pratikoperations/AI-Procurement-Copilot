"""Contract tests for governed cross-category multi-supplier allocation."""

from dataclasses import FrozenInstanceError
import json
import math

import pytest

from modules.allocation_contract import (
    ALLOCATION_CONTRACT_VERSION,
    CONTINUITY_SHARE_INTERPRETATION,
    FeasibilityStatus,
    MultiSupplierAllocationRequest,
    MultiSupplierFeasibilityResult,
    SupplierAllocationInput,
    normalize_controlled_bool,
    normalize_supplier_id,
)


def request(**overrides):
    values = {
        "annual_volume": 1000,
        "annual_volume_unit": "kg",
        "required_awardee_count": 2,
        "minimum_awarded_share_pct": 10,
        "maximum_supplier_share_pct": 70,
        "minimum_continuity_share_pct": 20,
        "minimum_risk_score": 55,
        "minimum_esg_score": 50,
        "capacity_utilization_ceiling_pct": 90,
        "category": "Packaging Procurement",
        "commodity": "Corrugated Board",
        "comparison_currency": "USD",
    }
    values.update(overrides)
    return MultiSupplierAllocationRequest(**values)


def test_request_is_versioned_and_immutable():
    value = request()
    assert value.contract_version == ALLOCATION_CONTRACT_VERSION
    with pytest.raises(FrozenInstanceError):
        value.required_awardee_count = 3


def test_request_normalizes_supplier_identifiers_and_serializes_stably():
    value = request(required_supplier_ids=(" Vendor B ", "VENDOR A", "vendor a"), excluded_supplier_ids=(" Vendor F ",))
    assert value.required_supplier_ids == ("vendor a", "vendor b")
    assert value.excluded_supplier_ids == ("vendor f",)
    assert value.to_json() == value.to_json()
    payload = json.loads(value.to_json())
    assert payload["contract_version"] == ALLOCATION_CONTRACT_VERSION
    assert payload["required_supplier_ids"] == ["vendor a", "vendor b"]


def test_request_rejects_unsupported_contract_version():
    with pytest.raises(ValueError, match="Unsupported contract_version"):
        request(contract_version="AIPC-MULTI-ALLOC-9.9")


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf, "1000", True])
def test_request_rejects_non_finite_or_non_numeric_annual_volume(value):
    with pytest.raises(ValueError, match="annual_volume"):
        request(annual_volume=value)


def test_request_rejects_non_integer_awardee_count():
    with pytest.raises(ValueError, match="integer"):
        request(required_awardee_count=2.5)


def test_request_requires_business_context_fields():
    with pytest.raises(ValueError, match="category is required"):
        request(category=" ")


def test_supplier_contract_supports_required_common_fields():
    value = SupplierAllocationInput(
        supplier_id=" Vendor A ", technical_eligible=True, adjusted_tco_unit_usd=1.1,
        total_score=88, risk_score=80, performance_score=90, esg_score=70,
        supplier_capacity=800, eligibility_failure_reasons=(),
        category_specific_eligibility_evidence={"plant_approved": True, "nested": {"line": "A"}},
    )
    assert value.supplier_id == "vendor a"
    assert value.supplier_capacity == 800
    assert value.category_specific_eligibility_evidence["plant_approved"] is True
    with pytest.raises(TypeError):
        value.category_specific_eligibility_evidence["plant_approved"] = False
    with pytest.raises(TypeError):
        value.category_specific_eligibility_evidence["nested"]["line"] = "B"


def test_supplier_mapping_accepts_existing_project_column_names():
    value = SupplierAllocationInput.from_mapping({
        "Supplier": "Vendor A", "technical_eligible": True, "adjusted_tco_unit_usd": 1.2,
        "total_score": 85, "risk_score": 75, "performance_score": 80, "esg_score": 65,
        "Supplier Capacity": 900, "technical_ineligibility_reasons": "",
    })
    assert value.supplier_id == "vendor a"
    assert value.supplier_capacity == 900


def test_supplier_contract_rejects_negative_capacity():
    with pytest.raises(ValueError, match="supplier_capacity"):
        SupplierAllocationInput(
            supplier_id="Vendor A", technical_eligible=True, adjusted_tco_unit_usd=1.1,
            total_score=88, risk_score=80, performance_score=90, esg_score=70, supplier_capacity=-1,
        )


def test_supplier_identifier_normalization_is_deterministic():
    assert normalize_supplier_id("  Vendor   A ") == "vendor a"
    with pytest.raises(ValueError):
        normalize_supplier_id(" ")


@pytest.mark.parametrize("value", [True, 1, "true", " True ", "yes", "1", "eligible", "Eligible"])
def test_controlled_boolean_true_values(value):
    assert normalize_controlled_bool(value) is True


@pytest.mark.parametrize("value", [False, 0, "false", " False ", "no", "0", "ineligible", "Ineligible"])
def test_controlled_boolean_false_values(value):
    assert normalize_controlled_bool(value) is False


@pytest.mark.parametrize("value", ["unknown", "approved", 2, None, [], {}])
def test_controlled_boolean_rejects_ambiguous_values(value):
    with pytest.raises(ValueError, match="explicit governed boolean"):
        normalize_controlled_bool(value)


def test_supplier_mapping_does_not_treat_false_string_as_true():
    value = SupplierAllocationInput.from_mapping({
        "Supplier": "Vendor A", "technical_eligible": "False", "Supplier Capacity": 900,
        "adjusted_tco_unit_usd": 1.2, "total_score": 85, "risk_score": 75,
        "performance_score": 80, "esg_score": 65,
    })
    assert value.technical_eligible is False


def test_feasibility_result_serialization_is_stable_human_reviewed_and_deeply_read_only():
    result = MultiSupplierFeasibilityResult(
        feasible=True, status_code=FeasibilityStatus.FEASIBLE, summary="Feasible",
        eligible_supplier_count=3, required_awardee_count=2, feasible_supplier_count=3,
        supplier_capacity_evidence=({"supplier_id": "vendor a", "nested": {"verified": False}},),
        maximum_feasible_share_by_supplier={"vendor a": 70.0}, blocking_reasons=(),
        warnings=("Human review required",), feasible_supplier_combinations=(("vendor a", "vendor b"),),
        binding_constraints=("capacity",),
    )
    assert result.human_review_required is True
    assert result.decision_complete is True
    assert result.continuity_share_interpretation == CONTINUITY_SHARE_INTERPRETATION
    with pytest.raises(TypeError):
        result.maximum_feasible_share_by_supplier["vendor a"] = 99
    with pytest.raises(TypeError):
        result.supplier_capacity_evidence[0]["nested"]["verified"] = True
    assert result.to_json() == result.to_json()
    payload = json.loads(result.to_json())
    assert payload["status_code"] == "FEASIBLE"
    assert payload["maximum_feasible_share_by_supplier"] == {"vendor a": 70.0}


def test_enumeration_limit_status_exists():
    assert FeasibilityStatus.ENUMERATION_LIMIT_REACHED.value == "ENUMERATION_LIMIT_REACHED"
