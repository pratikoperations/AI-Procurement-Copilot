"""Final Gate 2 validation tests for controlled source levels and mapping keys."""

import pytest

from modules.calculation_trace import deterministic_trace_id
from modules.parameter_precedence import (
    ParameterScopeValidationError,
    resolve_parameter,
)
from modules.parameter_profile_records import ParameterProfileRecord


def _record(record_id: str, source_level: str) -> ParameterProfileRecord:
    return ParameterProfileRecord(
        record_id,
        "ASM-001",
        1,
        "USD/kg",
        "USD/kg",
        None,
        None,
        None,
        source_level,
        "approved assumption",
    )


def test_unsupported_source_level_fails_with_controlled_error_not_keyerror():
    record = _record("bad-level", "regional_default")
    with pytest.raises(ParameterScopeValidationError) as captured:
        resolve_parameter("ASM-001", [record])
    message = str(captured.value)
    assert "bad-level" in message
    assert "regional_default" in message
    assert "global_default" in message
    assert "category_default" in message
    assert "supplier_specific" in message
    assert "rfq_scenario_override" in message
    assert not isinstance(captured.value, KeyError)


def test_non_string_mapping_key_fails_closed():
    with pytest.raises(TypeError, match="require string keys"):
        deterministic_trace_id({1: "numeric key"})


def test_string_and_integer_key_collision_fails_closed_without_data_loss():
    payload = {1: "numeric key", "1": "string key"}
    with pytest.raises(TypeError, match="require string keys"):
        deterministic_trace_id(payload)
    assert len(payload) == 2
    assert payload[1] == "numeric key"
    assert payload["1"] == "string key"


def test_string_key_mapping_insertion_order_does_not_change_trace_id():
    first = {"alpha": 1, "beta": {"x": 2, "y": 3}}
    second = {"beta": {"y": 3, "x": 2}, "alpha": 1}
    assert deterministic_trace_id(first) == deterministic_trace_id(second)


def test_volatile_string_keys_remain_excluded():
    first = {"value": 1, "timestamp": "2026-01-01T00:00:00Z"}
    second = {"value": 1, "timestamp": "2026-08-01T00:00:00Z"}
    assert deterministic_trace_id(first) == deterministic_trace_id(second)
