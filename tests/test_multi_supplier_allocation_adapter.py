from __future__ import annotations

from copy import deepcopy
from datetime import date, datetime, timezone
import json
import math
import warnings

import numpy as np
import pandas as pd
import pytest

from modules.allocation_contract import ALLOCATION_CONTRACT_VERSION
from modules.multi_supplier_allocation_adapter import (
    ADAPTER_VERSION,
    AdapterStatus,
    build_multi_supplier_allocation_adapter,
)


class UnsupportedEvidence:
    pass


class DeterministicMappingEvidence:
    def to_dict(self):
        return {"approved": True, "value": np.int64(7)}


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


def decoded(result):
    return json.loads(result.to_json())


@pytest.mark.parametrize(
    ("source_type", "origin", "ready", "expected_origin"),
    [
        ("synthetic_demo", None, True, "controlled_synthetic"),
        ("synthetic_demo", "controlled_synthetic", True, "controlled_synthetic"),
        ("synthetic_demo", "supplied", False, None),
        ("steel_synthetic", None, True, "controlled_synthetic"),
        ("steel_synthetic", "controlled_synthetic", True, "controlled_synthetic"),
        ("steel_synthetic", "supplied", False, None),
        ("uploaded_rfq", None, True, "supplied"),
        ("uploaded_rfq", "supplied", True, "supplied"),
        ("uploaded_rfq", "controlled_synthetic", False, None),
        ("governed_workbook", None, True, "governed_workbook"),
        ("governed_workbook", "governed_workbook", True, "governed_workbook"),
        ("governed_workbook", "controlled_synthetic", False, None),
        ("category_adapter", "controlled_synthetic", True, "controlled_synthetic"),
        ("category_adapter", "supplied", True, "supplied"),
        ("category_adapter", "governed_workbook", True, "governed_workbook"),
        ("category_adapter", None, False, None),
    ],
)
def test_source_origin_governance(source_type, origin, ready, expected_origin):
    data = frame()
    if source_type == "steel_synthetic":
        data = data.drop(columns=["adjusted_tco_unit_usd", "total_score"])
        data["normalized_usd_per_kg"] = [1.1 + i * 0.03 for i in range(len(data))]
        data["governed_total_score"] = [95 - i for i in range(len(data))]
    result = build(data, source_type=source_type, evidence_origin=origin)
    assert result.ready is ready
    payload = decoded(result)
    if ready:
        assert all(item["evidence_origin"] == expected_origin for item in payload["capacity_evidence"])
    else:
        assert result.status_code is AdapterStatus.INVALID_ROUTE_INPUT
        assert payload["ready"] is False


@pytest.mark.parametrize(
    ("source_type", "bad_origin", "required"),
    [
        ("uploaded_rfq", "controlled_synthetic", "supplied"),
        ("governed_workbook", "controlled_synthetic", "governed_workbook"),
        ("synthetic_demo", "supplied", "controlled_synthetic"),
        ("steel_synthetic", "supplied", "controlled_synthetic"),
    ],
)
def test_contradictory_origin_reason_is_deterministic(source_type, bad_origin, required):
    data = frame()
    if source_type == "steel_synthetic":
        data = data.drop(columns=["adjusted_tco_unit_usd", "total_score"])
        data["normalized_usd_per_kg"] = 1.1
        data["governed_total_score"] = 90.0
    result = build(data, source_type=source_type, evidence_origin=bad_origin)
    assert result.blocking_reasons == (
        f"source_type '{source_type}' requires evidence_origin '{required}'",
    )
    assert "0x" not in result.to_json()


@pytest.mark.parametrize(
    ("commodity", "category", "source_type", "origin"),
    [
        ("PET Resin", "Raw Material Procurement", "synthetic_demo", None),
        ("Flexible Laminates", "Packaging Procurement", "category_adapter", "supplied"),
        ("Kraft Paper", "Raw Material Procurement", "synthetic_demo", None),
        ("Corrugated Board", "Packaging Procurement", "synthetic_demo", None),
        ("Generic RFQ", "Other", "uploaded_rfq", None),
        ("Governed RFQ", "Other", "governed_workbook", None),
    ],
)
def test_cross_category_complete_evidence_is_valid(commodity, category, source_type, origin):
    data = frame()
    if commodity == "Flexible Laminates":
        data["Laminate Structure"] = "PET / PE"
        data["Application Approval Status"] = "Approved"
    if commodity == "Kraft Paper":
        data["GSM"] = 150
        data["Strength Grade"] = "22 BF"
        data["Kraft Variant"] = "Recycled Kraft"
    result = build(data, controls(category=category, commodity=commodity), source_type=source_type, evidence_origin=origin)
    assert result.ready
    decoded(result)


@pytest.mark.parametrize(
    ("column", "status"),
    [
        ("Supplier", AdapterStatus.MISSING_REQUIRED_COLUMN),
        ("technical_eligible", AdapterStatus.MISSING_TECHNICAL_ELIGIBILITY),
        ("adjusted_tco_unit_usd", AdapterStatus.MISSING_TCO_EVIDENCE),
        ("total_score", AdapterStatus.MISSING_SCORE_EVIDENCE),
        ("risk_score", AdapterStatus.MISSING_SCORE_EVIDENCE),
        ("performance_score", AdapterStatus.MISSING_SCORE_EVIDENCE),
        ("esg_score", AdapterStatus.MISSING_SCORE_EVIDENCE),
        ("Supplier Capacity", AdapterStatus.MISSING_SUPPLIER_CAPACITY),
    ],
)
def test_missing_required_columns_block(column, status):
    result = build(frame().drop(columns=[column]))
    assert not result.ready
    assert result.status_code is status
    decoded(result)


@pytest.mark.parametrize("value", ["maybe", "approved", 2, None, [], {}, object(), 3.5])
def test_ambiguous_technical_eligibility_blocks(value):
    data = frame()
    data["technical_eligible"] = data["technical_eligible"].astype(object)
    data.loc[0, "technical_eligible"] = value
    result = build(data)
    assert result.status_code is AdapterStatus.AMBIGUOUS_TECHNICAL_ELIGIBILITY
    decoded(result)


@pytest.mark.parametrize("value", [False, "False", "no", "0", 0, "ineligible"])
def test_controlled_false_values_remain_false(value):
    data = frame()
    data["technical_eligible"] = data["technical_eligible"].astype(object)
    data.loc[0, "technical_eligible"] = value
    result = build(data)
    assert result.ready
    supplier = next(item for item in result.supplier_inputs if item.supplier_id == "supplier a")
    assert supplier.technical_eligible is False


@pytest.mark.parametrize("value", [True, "True", "yes", "1", 1, "eligible"])
def test_controlled_true_values_remain_true(value):
    data = frame()
    data["technical_eligible"] = data["technical_eligible"].astype(object)
    data.loc[0, "technical_eligible"] = value
    result = build(data)
    assert result.ready
    supplier = next(item for item in result.supplier_inputs if item.supplier_id == "supplier a")
    assert supplier.technical_eligible is True


@pytest.mark.parametrize("column", ["adjusted_tco_unit_usd", "total_score", "risk_score", "performance_score", "esg_score"])
@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf, "bad"])
def test_invalid_numeric_evidence_blocks(column, value):
    data = frame()
    if isinstance(value, str):
        data[column] = data[column].astype(object)
    data.loc[0, column] = value
    result = build(data)
    expected = AdapterStatus.MISSING_TCO_EVIDENCE if column == "adjusted_tco_unit_usd" else AdapterStatus.MISSING_SCORE_EVIDENCE
    assert result.status_code is expected
    decoded(result)


@pytest.mark.parametrize("value", [0, -1, math.nan, math.inf, "bad", None])
def test_invalid_capacity_blocks(value):
    data = frame()
    if isinstance(value, str) or value is None:
        data["Supplier Capacity"] = data["Supplier Capacity"].astype(object)
    data.loc[0, "Supplier Capacity"] = value
    result = build(data)
    assert result.status_code is AdapterStatus.INVALID_SUPPLIER_CAPACITY
    decoded(result)


@pytest.mark.parametrize("unit", ["", "litre", None, "m2"])
def test_unsupported_unit_blocks(unit):
    result = build(control_values=controls(annual_volume_unit=unit))
    assert result.status_code is AdapterStatus.UNSUPPORTED_UNIT


@pytest.mark.parametrize("currency", ["INR", "EUR", "GBP", "JPY"])
def test_unsupported_currency_blocks(currency):
    result = build(control_values=controls(comparison_currency=currency))
    assert result.status_code is AdapterStatus.UNSUPPORTED_CURRENCY_BASIS


def test_valid_six_supplier_route_with_k3_and_versions():
    result = build()
    assert result.ready
    assert result.status_code is AdapterStatus.ADAPTER_READY
    assert result.adapter_version == ADAPTER_VERSION == "AIPC-MULTI-ALLOC-ADAPTER-1.0"
    assert result.request.contract_version == ALLOCATION_CONTRACT_VERSION == "AIPC-MULTI-ALLOC-1.0"
    assert len(result.supplier_inputs) == 6
    assert result.request.required_awardee_count == 3
    assert result.human_review_required is True


def test_valid_steel_aliases_map_correctly():
    data = frame().drop(columns=["adjusted_tco_unit_usd", "total_score"])
    data["normalized_usd_per_kg"] = [1.1 + i * 0.03 for i in range(len(data))]
    data["governed_total_score"] = [95 - i for i in range(len(data))]
    result = build(data, controls(commodity="Steel"), source_type="steel_synthetic")
    assert result.ready
    provenance = {item["canonical_field"]: item for item in result.field_provenance}
    assert provenance["adjusted_tco_unit_usd"]["mapping_type"] == "category adapter"
    assert provenance["total_score"]["source_column"] == "governed_total_score"


def test_explicit_alias_map_is_supported_but_not_inferred():
    data = frame().rename(columns={"Supplier Capacity": "Available Capacity"})
    blocked = build(data)
    accepted = build(data, column_aliases={"supplier_capacity": "Available Capacity"})
    assert blocked.status_code is AdapterStatus.MISSING_SUPPLIER_CAPACITY
    assert accepted.ready


def test_duplicate_normalized_supplier_ids_block():
    data = frame()
    data.loc[1, "Supplier"] = "  SUPPLIER   A "
    result = build(data)
    assert result.status_code is AdapterStatus.DUPLICATE_SUPPLIER_ID
    assert "Row 1" in result.blocking_reasons[0]


def test_required_and_excluded_supplier_ids_are_normalized():
    result = build(control_values=controls(required_supplier_ids=[" Supplier A "], excluded_supplier_ids=["SUPPLIER F"]))
    assert result.request.required_supplier_ids == ("supplier a",)
    assert result.request.excluded_supplier_ids == ("supplier f",)


def test_eligibility_reasons_and_category_evidence_are_preserved():
    data = frame()
    data["GSM"] = 150
    result = build(data)
    supplier_f = next(item for item in result.supplier_inputs if item.supplier_id == "supplier f")
    assert supplier_f.eligibility_failure_reasons == ("Capability gap",)
    assert result.supplier_inputs[0].category_specific_eligibility_evidence["GSM"] == 150


@pytest.mark.parametrize("missing_value", [math.nan, np.nan, pd.NA, pd.NaT])
def test_null_like_category_evidence_is_omitted_and_json_safe(missing_value):
    data = frame()
    data["GSM"] = pd.Series([missing_value] + [150] * (len(data) - 1), dtype=object)
    payload = decoded(build(data))
    evidence = payload["supplier_inputs"][0]["category_specific_eligibility_evidence"]
    assert "GSM" not in evidence


@pytest.mark.parametrize(
    ("column", "value", "expected_type"),
    [
        ("GSM", np.int64(150), int),
        ("Mill Allocation %", np.float64(70.5), float),
        ("Paint Line Capability", np.bool_(True), bool),
    ],
)
def test_numpy_scalars_normalize_to_python_types(column, value, expected_type):
    data = frame()
    data[column] = pd.Series([value] * len(data), dtype=object)
    payload = decoded(build(data))
    normalized = payload["supplier_inputs"][0]["category_specific_eligibility_evidence"][column]
    assert type(normalized) is expected_type


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (date(2026, 8, 2), "2026-08-02"),
        (datetime(2026, 8, 2, 10, 47, tzinfo=timezone.utc), "2026-08-02T10:47:00+00:00"),
        (pd.Timestamp("2026-08-02T10:47:00Z"), "2026-08-02T10:47:00+00:00"),
    ],
)
def test_supported_date_and_timestamp_evidence_is_deterministic(value, expected):
    data = frame()
    data["Application Approval"] = pd.Series([value] * len(data), dtype=object)
    first = decoded(build(data))
    second = decoded(build(data.sample(frac=1, random_state=7).reset_index(drop=True)))
    supplier_a_first = next(item for item in first["supplier_inputs"] if item["supplier_id"] == "supplier a")
    supplier_a_second = next(item for item in second["supplier_inputs"] if item["supplier_id"] == "supplier a")
    assert supplier_a_first["category_specific_eligibility_evidence"]["Application Approval"] == expected
    assert supplier_a_first == supplier_a_second


def test_supported_to_dict_evidence_is_normalized():
    data = frame()
    data["Application Approval"] = pd.Series([DeterministicMappingEvidence()] * len(data), dtype=object)
    payload = decoded(build(data))
    value = payload["supplier_inputs"][0]["category_specific_eligibility_evidence"]["Application Approval"]
    assert value == {"approved": True, "value": 7}


def test_unsupported_custom_object_returns_governed_json_safe_failure():
    data = frame()
    data["GSM"] = pd.Series([UnsupportedEvidence()] + [150] * (len(data) - 1), dtype=object)
    result = build(data)
    assert not result.ready
    assert result.status_code is AdapterStatus.CONTRACT_CONSTRUCTION_FAILURE
    reason = result.blocking_reasons[0]
    assert "Row 0" in reason
    assert "supplier 'supplier a'" in reason
    assert "field 'GSM'" in reason
    assert "UnsupportedEvidence" in reason
    assert "0x" not in reason
    payload = decoded(result)
    assert payload["ready"] is False
    assert payload["supplier_inputs"] == []


def test_unsupported_object_after_partial_processing_preserves_safe_partial_evidence():
    data = frame()
    values = [150, 160, UnsupportedEvidence(), 180, 190, 200]
    data["GSM"] = pd.Series(values, dtype=object)
    result = build(data)
    assert result.status_code is AdapterStatus.CONTRACT_CONSTRUCTION_FAILURE
    assert "Row 2" in result.blocking_reasons[0]
    payload = decoded(result)
    assert len(payload["eligibility_evidence"]) == 2
    assert len(payload["capacity_evidence"]) == 2


def test_sparse_evidence_and_row_order_are_deterministic():
    data = frame()
    data["GSM"] = pd.Series([150, pd.NA, 170, np.nan, 180, pd.NA], dtype=object)
    first = build(data)
    second = build(data.sample(frac=1, random_state=42).reset_index(drop=True))
    assert first.to_json() == second.to_json()


def test_source_dataframe_and_controls_are_not_mutated():
    data = frame()
    original_data = data.copy(deep=True)
    values = controls(required_supplier_ids=["Supplier A"])
    original_values = deepcopy(values)
    build(data, values)
    pd.testing.assert_frame_equal(data, original_data)
    assert values == original_values


def test_result_and_nested_evidence_are_immutable():
    result = build()
    with pytest.raises((AttributeError, TypeError)):
        result.ready = False
    with pytest.raises(TypeError):
        result.field_provenance[0]["source_column"] = "changed"
    with pytest.raises(TypeError):
        result.supplier_inputs[0].category_specific_eligibility_evidence["changed"] = True


def test_field_provenance_is_complete_and_deterministic():
    result = build()
    canonical = [item["canonical_field"] for item in result.field_provenance]
    assert canonical == sorted(canonical)
    assert set(canonical) == {
        "supplier_id", "technical_eligible", "adjusted_tco_unit_usd", "total_score",
        "risk_score", "performance_score", "esg_score", "supplier_capacity",
    }
    assert all(
        set(item) == {
            "canonical_field", "source_column", "source_type", "mapping_type",
            "evidence_class", "blocking_state", "evidence_note",
        }
        for item in result.field_provenance
    )


@pytest.mark.parametrize("status", list(AdapterStatus))
def test_status_values_are_stable_and_serializable(status):
    assert status.value == status.name


def test_failure_result_after_partial_processing_identifies_row_and_serializes():
    data = frame()
    data["Supplier Capacity"] = data["Supplier Capacity"].astype(object)
    data.loc[2, "Supplier Capacity"] = "bad"
    result = build(data)
    assert result.status_code is AdapterStatus.INVALID_SUPPLIER_CAPACITY
    assert "Row 2" in result.blocking_reasons[0]
    payload = decoded(result)
    assert len(payload["eligibility_evidence"]) == 2
    assert len(payload["capacity_evidence"]) == 2


def test_synthetic_warning_only_for_controlled_synthetic_origin():
    synthetic = build(source_type="category_adapter", evidence_origin="controlled_synthetic")
    supplied = build(source_type="category_adapter", evidence_origin="supplied")
    governed = build(source_type="category_adapter", evidence_origin="governed_workbook")
    assert any("Controlled synthetic" in warning for warning in synthetic.warnings)
    assert not any("Controlled synthetic" in warning for warning in supplied.warnings)
    assert not any("Controlled synthetic" in warning for warning in governed.warnings)


def test_no_capacity_or_eligibility_defaults_exist():
    missing_capacity = build(frame().drop(columns=["Supplier Capacity"]))
    missing_eligibility = build(frame().drop(columns=["technical_eligible"]))
    assert missing_capacity.supplier_inputs == ()
    assert missing_eligibility.supplier_inputs == ()
    assert not missing_capacity.ready and not missing_eligibility.ready


def test_adapter_does_not_call_feasibility_or_allocation_engine():
    result = build()
    assert result.ready
    assert not hasattr(result, "feasibility_result")
    assert not hasattr(result, "allocation_result")


def test_request_construction_failure_is_governed_and_json_safe():
    result = build(control_values=controls(required_awardee_count="three"))
    assert result.status_code is AdapterStatus.CONTRACT_CONSTRUCTION_FAILURE
    assert result.request is None
    decoded(result)


def test_invalid_dataframe_and_source_type_are_governed():
    empty = build(pd.DataFrame())
    unsupported = build(source_type="unknown")
    assert empty.status_code is AdapterStatus.INVALID_ROUTE_INPUT
    assert unsupported.status_code is AdapterStatus.INVALID_ROUTE_INPUT
    decoded(empty)
    decoded(unsupported)


def test_deliberate_mixed_type_fixtures_emit_no_pandas_dtype_warning():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        data = frame()
        data["technical_eligible"] = data["technical_eligible"].astype(object)
        data.loc[0, "technical_eligible"] = "maybe"
        numeric = frame()
        numeric["risk_score"] = numeric["risk_score"].astype(object)
        numeric.loc[0, "risk_score"] = "bad"
    assert not [item for item in caught if "incompatible dtype" in str(item.message)]
