"""Source-preserving currency and unit normalization for v1.3 canonical RFQ records."""
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping


@dataclass(frozen=True)
class NormalizationResult:
    normalized_values: Mapping[str, Any]
    status: str
    blockers: tuple[str, ...]
    provenance: tuple[str, ...]


def _decimal(value: Any) -> Decimal | None:
    if value is None or str(value).strip() == "":
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None


def normalize_record(values: Mapping[str, Any], *, comparison_currency: str | None, quantity_field: str, uom_field: str, price_field: str) -> NormalizationResult:
    blockers: list[str] = []
    provenance: list[str] = []
    quantity = _decimal(values.get(quantity_field))
    price = _decimal(values.get(price_field))
    price_unit = _decimal(values.get("PRICE_UNIT"))
    source_uom = str(values.get(uom_field) or "").strip()
    comparison_uom = str(values.get("COMPARISON_UOM") or "").strip()
    source_currency = str(values.get("CURRENCY") or "").strip().upper()
    target_currency = str(comparison_currency or "").strip().upper()
    factor = Decimal("1")
    fx = Decimal("1")

    if not target_currency:
        blockers.append("COMPARISON_CURRENCY_REQUIRED")
    if not source_currency:
        blockers.append("SOURCE_CURRENCY_REQUIRED")
    if source_uom and comparison_uom and source_uom != comparison_uom:
        factor = _decimal(values.get("UOM_CONVERSION_FACTOR")) or Decimal("0")
        if factor <= 0:
            blockers.append("UOM_CONVERSION_FACTOR_REQUIRED")
        else:
            provenance.append("UOM_CONVERSION_FACTOR")
    elif source_uom and comparison_uom:
        provenance.append("SAME_UOM_FACTOR_1")
    else:
        blockers.append("UOM_REQUIRED")

    if source_currency and target_currency and source_currency != target_currency:
        fx = _decimal(values.get("EXCHANGE_RATE")) or Decimal("0")
        if fx <= 0 or not values.get("EXCHANGE_RATE_DATE"):
            blockers.append("FX_RATE_AND_DATE_REQUIRED")
        else:
            provenance.extend(("EXCHANGE_RATE", "EXCHANGE_RATE_DATE"))
    elif source_currency and target_currency:
        provenance.append("SAME_CURRENCY_RATE_1")

    normalized_quantity = quantity * factor if quantity is not None and factor > 0 else None
    source_unit_price = price / price_unit if price is not None and price_unit and price_unit > 0 else None
    normalized_unit_price = source_unit_price / factor / fx if source_unit_price is not None and factor > 0 and fx > 0 else None

    normalized = {
        "SOURCE_QUANTITY": quantity,
        "NORMALIZED_QUANTITY": normalized_quantity,
        "SOURCE_UOM": source_uom or None,
        "COMPARISON_UOM": comparison_uom or None,
        "UOM_CONVERSION_FACTOR_USED": factor if factor > 0 else None,
        "SOURCE_PRICE": price,
        "PRICE_UNIT": price_unit,
        "SOURCE_CURRENCY": source_currency or None,
        "COMPARISON_CURRENCY": target_currency or None,
        "EXCHANGE_RATE_USED": fx if fx > 0 else None,
        "EXCHANGE_RATE_DATE_USED": values.get("EXCHANGE_RATE_DATE"),
        "NORMALIZED_UNIT_PRICE": normalized_unit_price,
    }
    return NormalizationResult(normalized, "BLOCKED" if blockers else "NORMALIZED", tuple(dict.fromkeys(blockers)), tuple(provenance))
