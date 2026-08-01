"""Final Gate 2 validation tests for controlled source levels and mapping keys."""

from types import SimpleNamespace

import pytest

from modules.calculation_trace import deterministic_trace_id
from modules.parameter_precedence import (
    ParameterScopeValidationError,
    resolve_parameter,
)


def _malformed_source_level_record():
    """Bypass the profile model's own guard to test the resolver boundary directly."""
    return SimpleNamespace(
        parameter_record_id="bad-level",
        assumption_id="ASM-001",
        value=1,
        canonical_unit="USD/kg",
        original_unit="USD/kg",
        category=None,
        supplier=None,
        rfq_scenario=None,
        source_level="regional_default",
        evidence_classification="approved assumption",
        source_reference=None,
        effective_date=None,
        review_expiry_date=None,
        confidence=None,
        override_status="not_overridden",
        override_reason=None,
        approver=None,
        version="1.0",
    )


def test_unsupported_source_level_fails_with_controlled_error_not_keyerror():
    record = _malformed_source_level_record()
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
