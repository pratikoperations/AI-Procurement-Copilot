from __future__ import annotations

from copy import deepcopy
import json
import math

import pandas as pd
import pytest

from modules.allocation_contract import ALLOCATION_CONTRACT_VERSION
from modules.multi_supplier_allocation_adapter import (
    ADAPTER_VERSION,
    AdapterStatus,
    build_multi_supplier_allocation_adapter,
)

pytestmark = pytest.mark.filterwarnings(
    "ignore:Setting an item of incompatible dtype is deprecated:FutureWarning"
)


def controls(**overrides):
    values = {
        "annual_volume": 1000.0,
        "annual_volume_unit": "kg",
        "required_awardee_count": 3,
        "minimum_awarded_share_pct": 10.0,
        "maximum_supplier_share_pct": 60.0,
        "minimum_continuity_share_pct": 15.0,
        "minimum_risk_score": 55.0,
        "minimum_esg_score": 50.0,
        "capacity_utilization_ceiling_pct": 90.0,
        "category": "Raw Material Procurement",
        "commodity": "PET Resin",
        "comparison_currency": "USD",
        "required_supplier_ids": (),
        "excluded_supplier_ids": (),
    }
    values.update(overrides)
    return values


def frame(count=6, **overrides):
    rows = []
    for index in range(count):
        rows.append(
            {
                "Supplier": f"Supplier {chr(65 + index)}",
                "technical_eligible": index != count - 1,
                "adjusted_tco_unit_usd": 1.0 + index * 0.05,
                "total_score": 90.0 - index,
                "risk_score": 80.0 - index,
                "performance_score": 85.0 - index,
                "esg_score": 75.0 - index,
                "Supplier Capacity": 700.0 + index * 50,
                "technical_ineligibility_reasons": "Capability gap" if index == count - 1 else "",
            }
        )
    result = pd.DataFrame(rows)
    for key, value in overrides.items():
        result[key] = value
    return result


def build(data=None, control_values=None, **kwargs):
    return build_multi_supplier_allocation_adapter(
        frame() if data is None else data,
        controls() if control_values is None else control_values,
        route_name=kwargs.pop("route_name", "test-route"),
        source_type=kwargs.pop("source_type", "synthetic_demo"),
        **kwargs,
    )


def test_valid_six_supplier_route_with_k3():
    result = build()
    assert result.ready
    assert result.status_code is AdapterStatus.ADAPTER_READY
    assert len(result.supplier_inputs) == 6
    assert result.request.required_awardee_count == 3


@pytest.mark.parametrize(
    ("commodity", "category", "source_type"),
    [
        ("PET Resin", "Raw Material Procurement", "synthetic_demo"),
        ("Flexible Laminates", "Packaging Procurement", "category_adapter"),
        ("Kraft Paper", "Raw Material Procurement", "synthetic_demo"),
        ("Corrugated Board", "Packaging Procurement", "synthetic_demo"),
        ("Generic RFQ", "Other", "uploaded_rfq"),
    ],
)
def test_cross_category_complete_evidence_is_valid(commodity, category, source_type):
    data = frame()
    if commodity == "Flexible Laminates":
        data["Laminate Structure"] = "PET / PE"
        data["Application Approval Status"] = "Approved"
    if commodity == "Kraft Paper":
        data["GSM"] = 150
        data["Strength Grade"] = "22 BF"
        data["Kraft Variant"] = "Recycled Kraft"
    result = build(data, controls(category=category, commodity=commodity), source_type=source_type)
    assert result.ready


def test_valid_governed_workbook_with_complete_evidence():
    result = build(source_type="governed_workbook")
    assert result.ready
    assert not result.controlled_defaults_used


def test_valid_uploaded_rfq_with_complete_evidence():
    result = build(source_type="uploaded_rfq")
    assert result.ready
    assert all("controlled synthetic" not in item["evidence_note"].lower() for item in result.capacity_evidence)


def test_valid_steel_scored_route_uses_controlled_aliases():
    data = frame().drop(columns=["adjusted_tco_unit_usd", "total_score"])
    data["normalized_usd_per_kg"] = [1.1 + i * 0.03 for i in range(len(data))]
    data["governed_total_score"] = [95 - i for i in range(len(data))]
    data["eligibility_failure_reasons"] = ["" for _ in range(len(data))]
    data["Supported Steel Profiles"] = "CR_COIL_COMMERCIAL"
    result = build(
        data,
        controls(commodity="Steel"),
        source_type="steel_synthetic",
    )
    assert result.ready
    assert result.supplier_inputs[0].adjusted_tco_unit_usd == pytest.approx(1.1)
    assert result.supplier_inputs[0].total_score == pytest.approx(95)
    provenance = {item["canonical_field"]: item for item in result.field_provenance}
    assert provenance["adjusted_tco_unit_usd"]["mapping_type"] == "category adapter"
    assert provenance["total_score"]["source_column"] == "governed_total_score"


@pytest.mark.parametrize("source_type", ["synthetic_demo", "uploaded_rfq", "governed_workbook"])
def test_missing_technical_eligibility_blocks(source_type):
    result = build(frame().drop(columns=["technical_eligible"]), source_type=source_type)
    assert not result.ready
    assert result.status_code is AdapterStatus.MISSING_TECHNICAL_ELIGIBILITY


@pytest.mark.parametrize("source_type", ["synthetic_demo", "uploaded_rfq", "governed_workbook"])
def test_missing_capacity_blocks_without_annual_volume_default(source_type):
    result = build(frame().drop(columns=["Supplier Capacity"]), source_type=source_type)
    assert not result.ready
    assert result.status_code is AdapterStatus.MISSING_SUPPLIER_CAPACITY
    assert result.supplier_inputs == ()


def test_corrugated_synthetic_missing_eligibility_blocks():
    result = build(
        frame().drop(columns=["technical_eligible"]),
        controls(category="Packaging Procurement", commodity="Corrugated Board"),
    )
    assert result.status_code is AdapterStatus.MISSING_TECHNICAL_ELIGIBILITY


def test_corrugated_synthetic_missing_capacity_blocks():
    result = build(
        frame().drop(columns=["Supplier Capacity"]),
        controls(category="Packaging Procurement", commodity="Corrugated Board"),
    )
    assert result.status_code is AdapterStatus.MISSING_SUPPLIER_CAPACITY


@pytest.mark.parametrize("value", ["maybe", "approved", 2, None])
def test_ambiguous_technical_eligibility_blocks(value):
    data = frame()
    data.loc[0, "technical_eligible"] = value
    result = build(data)
    assert result.status_code is AdapterStatus.AMBIGUOUS_TECHNICAL_ELIGIBILITY


def test_string_false_remains_false():
    data = frame()
    data.loc[0, "technical_eligible"] = "False"
    result = build(data)
    supplier = next(item for item in result.supplier_inputs if item.supplier_id == "supplier a")
    assert supplier.technical_eligible is False


def test_no_technical_eligibility_default_to_true():
    result = build(frame().drop(columns=["technical_eligible"]))
    assert result.supplier_inputs == ()
    assert not result.ready


def test_duplicate_normalized_supplier_ids_block():
    data = frame()
    data.loc[1, "Supplier"] = "  SUPPLIER   A "
    result = build(data)
    assert result.status_code is AdapterStatus.DUPLICATE_SUPPLIER_ID


@pytest.mark.parametrize(
    ("column", "status"),
    [
        ("adjusted_tco_unit_usd", AdapterStatus.MISSING_TCO_EVIDENCE),
        ("total_score", AdapterStatus.MISSING_SCORE_EVIDENCE),
        ("risk_score", AdapterStatus.MISSING_SCORE_EVIDENCE),
        ("performance_score", AdapterStatus.MISSING_SCORE_EVIDENCE),
        ("esg_score", AdapterStatus.MISSING_SCORE_EVIDENCE),
    ],
)
def test_missing_tco_or_score_columns_block(column, status):
    result = build(frame().drop(columns=[column]))
    assert result.status_code is status


@pytest.mark.parametrize("column", ["adjusted_tco_unit_usd", "total_score", "risk_score", "performance_score", "esg_score"])
@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf, "bad"])
def test_invalid_numeric_evidence_blocks(column, value):
    data = frame()
    data.loc[0, column] = value
    result = build(data)
    expected = AdapterStatus.MISSING_TCO_EVIDENCE if column == "adjusted_tco_unit_usd" else AdapterStatus.MISSING_SCORE_EVIDENCE
    assert result.status_code is expected


@pytest.mark.parametrize("value", [0, -1, math.nan, math.inf, "bad", None])
def test_invalid_capacity_blocks(value):
    data = frame()
    data.loc[0, "Supplier Capacity"] = value
    result = build(data)
    assert result.status_code is AdapterStatus.INVALID_SUPPLIER_CAPACITY


def test_unsupported_comparison_currency_blocks():
    result = build(control_values=controls(comparison_currency="INR"))
    assert result.status_code is AdapterStatus.UNSUPPORTED_CURRENCY_BASIS


@pytest.mark.parametrize("unit", ["", "litre", None])
def test_unsupported_unit_blocks(unit):
    result = build(control_values=controls(annual_volume_unit=unit))
    assert result.status_code is AdapterStatus.UNSUPPORTED_UNIT


def test_explicit_alias_map_is_supported():
    data = frame().rename(columns={"Supplier Capacity": "Available Capacity"})
    result = build(data, column_aliases={"supplier_capacity": "Available Capacity"})
    assert result.ready
    provenance = {item["canonical_field"]: item for item in result.field_provenance}
    assert provenance["supplier_capacity"]["mapping_type"] == "explicit alias"


def test_alias_is_not_inferred_without_explicit_map():
    data = frame().rename(columns={"Supplier Capacity": "Available Capacity"})
    result = build(data)
    assert result.status_code is AdapterStatus.MISSING_SUPPLIER_CAPACITY


def test_eligibility_reasons_are_preserved():
    result = build()
    supplier = next(item for item in result.supplier_inputs if item.supplier_id == "supplier f")
    assert supplier.eligibility_failure_reasons == ("Capability gap",)


def test_flexible_laminate_category_evidence_is_preserved():
    data = frame()
    data["Laminate Structure"] = "PET / PE"
    data["Application Approval Status"] = "Approved"
    result = build(data, controls(category="Packaging Procurement", commodity="Flexible Laminates"), source_type="category_adapter")
    evidence = result.supplier_inputs[0].category_specific_eligibility_evidence
    assert evidence["Laminate Structure"] == "PET / PE"
    assert evidence["Application Approval Status"] == "Approved"


def test_kraft_category_evidence_is_preserved():
    data = frame()
    data["GSM"] = 150
    data["Strength Grade"] = "22 BF"
    data["Kraft Variant"] = "Recycled Kraft"
    data["Mill Allocation %"] = 70
    result = build(data, controls(commodity="Kraft Paper"))
    evidence = result.supplier_inputs[0].category_specific_eligibility_evidence
    assert evidence["GSM"] == 150
    assert evidence["Strength Grade"] == "22 BF"


def test_synthetic_evidence_is_labelled_controlled_demonstration():
    result = build()
    assert any("Controlled synthetic demonstration assumption" in warning for warning in result.warnings)
    assert all("Controlled synthetic demonstration assumption" in item["evidence_note"] for item in result.capacity_evidence)


def test_uploaded_data_never_receives_synthetic_defaults():
    result = build(source_type="uploaded_rfq")
    assert result.controlled_defaults_used == ()
    assert not any("Controlled synthetic" in warning for warning in result.warnings)


def test_contract_and_adapter_versions_are_stable():
    result = build()
    assert result.adapter_version == ADAPTER_VERSION
    assert ADAPTER_VERSION == "AIPC-MULTI-ALLOC-ADAPTER-1.0"
    assert result.request.contract_version == ALLOCATION_CONTRACT_VERSION
    assert ALLOCATION_CONTRACT_VERSION == "AIPC-MULTI-ALLOC-1.0"


def test_supplier_input_order_is_deterministic():
    result = build(frame().iloc[::-1].reset_index(drop=True))
    assert [item.supplier_id for item in result.supplier_inputs] == sorted(item.supplier_id for item in result.supplier_inputs)


def test_row_order_does_not_change_serialization():
    first = build(frame())
    second = build(frame().sample(frac=1, random_state=42).reset_index(drop=True))
    assert first.to_json() == second.to_json()


def test_source_dataframe_is_not_mutated():
    data = frame()
    original = data.copy(deep=True)
    build(data)
    pd.testing.assert_frame_equal(data, original)


def test_controls_mapping_is_not_mutated():
    values = controls(required_supplier_ids=["Supplier A"])
    original = deepcopy(values)
    build(control_values=values)
    assert values == original


def test_adapter_result_and_nested_evidence_are_read_only():
    result = build()
    with pytest.raises((AttributeError, TypeError)):
        result.ready = False
    with pytest.raises(TypeError):
        result.field_provenance[0]["source_column"] = "changed"
    with pytest.raises(TypeError):
        result.supplier_inputs[0].category_specific_eligibility_evidence["changed"] = True


def test_strict_json_serialization_is_deterministic():
    result = build()
    first = result.to_json()
    second = result.to_json()
    assert first == second
    decoded = json.loads(first)
    assert decoded["status_code"] == "ADAPTER_READY"
    assert decoded["human_review_required"] is True


def test_field_provenance_is_deterministic_and_complete():
    result = build()
    canonical = [item["canonical_field"] for item in result.field_provenance]
    assert canonical == sorted(canonical)
    assert set(canonical) == {
        "supplier_id", "technical_eligible", "adjusted_tco_unit_usd", "total_score",
        "risk_score", "performance_score", "esg_score", "supplier_capacity",
    }
    assert all(set(item) == {"canonical_field", "source_column", "source_type", "mapping_type", "evidence_class", "blocking_state", "evidence_note"} for item in result.field_provenance)


def test_non_empty_dataframe_is_required():
    result = build(pd.DataFrame())
    assert result.status_code is AdapterStatus.INVALID_ROUTE_INPUT


def test_supported_source_type_is_required():
    result = build(source_type="unknown")
    assert result.status_code is AdapterStatus.INVALID_ROUTE_INPUT


def test_request_construction_failure_is_governed():
    result = build(control_values=controls(required_awardee_count="three"))
    assert result.status_code is AdapterStatus.CONTRACT_CONSTRUCTION_FAILURE
    assert result.request is None


def test_required_and_excluded_supplier_ids_are_normalized():
    result = build(control_values=controls(required_supplier_ids=[" Supplier A "], excluded_supplier_ids=["SUPPLIER F"]))
    assert result.request.required_supplier_ids == ("supplier a",)
    assert result.request.excluded_supplier_ids == ("supplier f",)


def test_human_review_remains_mandatory():
    result = build()
    assert result.human_review_required is True


def test_adapter_does_not_call_feasibility_or_allocation_engine():
    result = build()
    assert result.ready
    assert not hasattr(result, "feasibility_result")
    assert not hasattr(result, "allocation_result")
