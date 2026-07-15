import pandas as pd
import pytest

from modules.utils import (
    build_currency_display_frame,
    currency_label,
    format_money,
    normalize_display_currency,
    unit_cost,
)


def test_display_currency_modes_are_governed():
    assert normalize_display_currency("usd") == "USD"
    assert normalize_display_currency("INR") == "INR"
    assert normalize_display_currency("both") == "Both"
    assert currency_label("Both") == "USD / INR"

    with pytest.raises(ValueError, match="Unsupported display currency"):
        normalize_display_currency("EUR")


def test_money_formatting_respects_selected_currency():
    assert format_money(100, "USD", 83) == "$100"
    assert format_money(100, "INR", 83) == "₹8,300"
    assert format_money(100, "Both", 83) == "$100 / ₹8,300"


def test_unit_cost_respects_selected_currency_without_double_conversion():
    assert unit_cost(2, "USD", 83) == "$2.0000"
    assert unit_cost(2, "INR", 83) == "₹166.00"
    assert unit_cost(2, "Both", 83) == "$2.0000 / ₹166.00"


def test_currency_display_frame_usd_mode():
    source = pd.DataFrame({"Supplier": ["A"], "annual_tco_usd": [100.0]})

    result = build_currency_display_frame(
        source,
        {"annual_tco_usd": "Annual TCO"},
        "USD",
        83,
    )

    assert list(result.columns) == ["Supplier", "Annual TCO (USD)"]
    assert result.loc[0, "Annual TCO (USD)"] == 100.0
    assert "annual_tco_usd" in source.columns


def test_currency_display_frame_inr_mode():
    source = pd.DataFrame({"Supplier": ["A"], "annual_tco_usd": [100.0]})

    result = build_currency_display_frame(
        source,
        {"annual_tco_usd": "Annual TCO"},
        "INR",
        83,
    )

    assert list(result.columns) == ["Supplier", "Annual TCO (INR)"]
    assert result.loc[0, "Annual TCO (INR)"] == 8300.0


def test_currency_display_frame_both_mode():
    source = pd.DataFrame({"Supplier": ["A"], "annual_tco_usd": [100.0]})

    result = build_currency_display_frame(
        source,
        {"annual_tco_usd": "Annual TCO"},
        "Both",
        83,
    )

    assert list(result.columns) == [
        "Supplier",
        "Annual TCO (USD)",
        "Annual TCO (INR)",
    ]
    assert result.loc[0, "Annual TCO (USD)"] == 100.0
    assert result.loc[0, "Annual TCO (INR)"] == 8300.0
