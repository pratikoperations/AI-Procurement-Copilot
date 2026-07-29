from datetime import date
from decimal import Decimal

import pytest

from modules.rfq_normalization_bridge import normalize_record


def normalize(values, currency="INR", quantity_field="QUOTED_QUANTITY", price_field="BASE_UNIT_PRICE", uom_field="QUOTATION_UOM"):
    return normalize_record(
        values,
        comparison_currency=currency,
        quantity_field=quantity_field,
        uom_field=uom_field,
        price_field=price_field,
    )


def base():
    return {
        "QUOTED_QUANTITY": 10,
        "BASE_UNIT_PRICE": 100,
        "PRICE_UNIT": 1,
        "QUOTATION_UOM": "EA",
        "COMPARISON_UOM": "EA",
        "CURRENCY": "INR",
    }


def test_same_basis_preserves_source():
    result = normalize(base())
    assert result.status == "NORMALIZED"
    assert result.normalized_values["SOURCE_PRICE"] == Decimal("100")
    assert result.normalized_values["NORMALIZED_UNIT_PRICE"] == Decimal("100")


def test_uom_quantity_multiplies_price_divides():
    values = base() | {"BASE_UNIT_PRICE": 1000, "QUOTATION_UOM": "BOX", "UOM_CONVERSION_FACTOR": 100}
    result = normalize(values)
    assert result.normalized_values["NORMALIZED_QUANTITY"] == Decimal("1000")
    assert result.normalized_values["NORMALIZED_UNIT_PRICE"] == Decimal("10")


def test_fx_divides_source_currency_per_target():
    values = base() | {"QUOTED_QUANTITY": 1, "BASE_UNIT_PRICE": 8300, "EXCHANGE_RATE": 83, "EXCHANGE_RATE_DATE": date(2026, 7, 1)}
    result = normalize(values, currency="USD")
    assert result.normalized_values["NORMALIZED_UNIT_PRICE"] == Decimal("100")


def test_missing_fx_blocks():
    values = base() | {"CURRENCY": "EUR"}
    assert "FX_RATE_AND_DATE_REQUIRED" in normalize(values).blockers


def test_no_silent_currency_default():
    assert "COMPARISON_CURRENCY_REQUIRED" in normalize(base(), currency=None).blockers


@pytest.mark.parametrize("price_unit", [None, 0, -1, "bad"])
def test_invalid_price_unit_blocks(price_unit):
    values = base() | {"PRICE_UNIT": price_unit}
    assert "PRICE_UNIT_INVALID" in normalize(values).blockers


@pytest.mark.parametrize("quantity", [None, 0, -1, "bad"])
def test_invalid_quantity_blocks(quantity):
    values = base() | {"QUOTED_QUANTITY": quantity}
    assert "SOURCE_QUANTITY_INVALID" in normalize(values).blockers


@pytest.mark.parametrize("price", [None, -1, "bad"])
def test_invalid_source_price_blocks(price):
    values = base() | {"BASE_UNIT_PRICE": price}
    assert "SOURCE_PRICE_INVALID" in normalize(values).blockers


def test_zero_price_is_allowed_by_non_negative_contract():
    result = normalize(base() | {"BASE_UNIT_PRICE": 0})
    assert "SOURCE_PRICE_INVALID" not in result.blockers
    assert result.normalized_values["NORMALIZED_UNIT_PRICE"] == Decimal("0")


def test_invalid_po_history_price_basis_blocks():
    values = {
        "ORDER_QUANTITY": 100,
        "NET_PRICE": 10,
        "PRICE_UNIT": 0,
        "ORDER_UOM": "EA",
        "COMPARISON_UOM": "EA",
        "CURRENCY": "INR",
    }
    result = normalize(values, quantity_field="ORDER_QUANTITY", price_field="NET_PRICE", uom_field="ORDER_UOM")
    assert result.status == "BLOCKED" and "PRICE_UNIT_INVALID" in result.blockers