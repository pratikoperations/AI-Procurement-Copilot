"""Contracts for readable canonical payload presentation."""
from modules.calculation_explorer_currency_ui import prepare_canonical_payload_rows


def test_canonical_payload_rows_are_human_readable_and_complete() -> None:
    payload = {
        "target_unit_cost_usd": 1.27,
        "commodity": "PET Resin",
        "breakdown": {"freight": 0.05, "duty": 0.03},
    }

    rows = prepare_canonical_payload_rows(payload)

    assert rows == [
        {"Field": "Target Unit Cost USD", "Value": "1.27"},
        {"Field": "Commodity", "Value": "PET Resin"},
        {"Field": "Breakdown › Freight", "Value": "0.05"},
        {"Field": "Breakdown › Duty", "Value": "0.03"},
    ]


def test_canonical_payload_rows_handle_scalar_payload() -> None:
    assert prepare_canonical_payload_rows(4.2) == [
        {"Field": "Result", "Value": "4.20"}
    ]
