"""Versioned evidence coverage for v1.3 sourcing analysis."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping, Sequence

POLICY_VERSION = "AIPC-EVIDENCE-COVERAGE-1.3.0"
WEIGHTS = {
    "comparable_price": Decimal("25"),
    "quantity_availability": Decimal("15"),
    "commercial_terms": Decimal("10"),
    "delivery": Decimal("10"),
    "quality": Decimal("10"),
    "risk": Decimal("10"),
    "esg": Decimal("5"),
    "historical_benchmark": Decimal("15"),
}


@dataclass(frozen=True)
class EvidenceCoverage:
    policy_version: str
    dimension_results: Mapping[str, bool]
    coverage_percent: Decimal
    aggregation_method: str


def _decimal(value: Any) -> Decimal | None:
    try:
        if value is None or str(value).strip() == "":
            return None
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None


def _score_valid(value: Any) -> bool:
    score = _decimal(value)
    return score is not None and Decimal("0") <= score <= Decimal("100")


def _meaningful_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _meaningful_charge(value: Any) -> bool:
    amount = _decimal(value)
    return amount is not None and amount != 0


def quotation_coverage(
    values: Mapping[str, Any],
    normalized: Mapping[str, Any],
    *,
    has_history_match: bool,
) -> EvidenceCoverage:
    quoted = _decimal(values.get("QUOTED_QUANTITY"))
    requested = _decimal(values.get("REQUESTED_QUANTITY"))
    full_quantity = values.get("FULL_QUANTITY_AVAILABLE") is True
    commercial_text = any(_meaningful_text(values.get(k)) for k in ("INCOTERMS_CODE", "PAYMENT_TERMS_CODE"))
    commercial_charge = any(_meaningful_charge(values.get(k)) for k in ("FREIGHT_AMOUNT", "PACKING_AMOUNT", "DISCOUNT_AMOUNT"))
    lead_time = _decimal(values.get("LEAD_TIME_DAYS"))
    delivery = (lead_time is not None and lead_time >= 0) or values.get("PROMISED_DELIVERY_DATE") is not None
    quality = values.get("TECHNICALLY_APPROVED") is True or _score_valid(values.get("QUALITY_SCORE"))
    dims = {
        "comparable_price": _decimal(normalized.get("NORMALIZED_UNIT_PRICE")) is not None,
        "quantity_availability": quoted is not None and requested is not None and quoted > 0 and requested > 0 and (full_quantity or quoted >= requested),
        "commercial_terms": commercial_text or commercial_charge,
        "delivery": delivery,
        "quality": quality,
        "risk": _score_valid(values.get("RISK_SCORE")),
        "esg": _score_valid(values.get("ESG_SCORE")),
        "historical_benchmark": bool(has_history_match),
    }
    coverage = sum(weight for name, weight in WEIGHTS.items() if dims[name])
    return EvidenceCoverage(POLICY_VERSION, dims, coverage, "PER_QUOTATION")


def aggregate_item(coverages: Sequence[EvidenceCoverage]) -> EvidenceCoverage:
    if not coverages:
        return EvidenceCoverage(POLICY_VERSION, {key: False for key in WEIGHTS}, Decimal("0"), "NO_VALID_QUOTATIONS")
    minimum = min(coverages, key=lambda item: item.coverage_percent)
    return EvidenceCoverage(POLICY_VERSION, minimum.dimension_results, minimum.coverage_percent, "MINIMUM_VALID_SUPPLIER_COVERAGE")


def aggregate_event(
    item_results: Mapping[str, EvidenceCoverage],
    item_quantities: Mapping[str, Any],
) -> tuple[Decimal, str]:
    if not item_results:
        return Decimal("0"), "NO_ITEMS"
    usable: dict[str, Decimal] = {}
    for key in item_results:
        quantity = _decimal(item_quantities.get(key))
        if quantity is not None and quantity > 0:
            usable[key] = quantity
    if len(usable) == len(item_results):
        total = sum(usable.values())
        return (
            sum(item_results[key].coverage_percent * usable[key] for key in item_results) / total,
            "REQUESTED_QUANTITY_WEIGHTED",
        )
    return (
        sum(result.coverage_percent for result in item_results.values()) / Decimal(len(item_results)),
        "EQUAL_ITEM_WEIGHTED_FALLBACK",
    )