"""Review-only compatibility assessment for governed v1.3 RFQ workbooks."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any

import pandas as pd

MANIFEST_VERSION = "AIPC-LEGACY-COMPATIBILITY-MANIFEST-1.3.0"
GOVERNED_RANKING_INPUTS_NOT_CANONICAL = "GOVERNED_RANKING_INPUTS_NOT_CANONICAL"
REVIEW_ONLY = "REVIEW_ONLY"
SUPPLIED = "SUPPLIED"
DERIVED = "DERIVED"
EXCLUDED = "EXCLUDED"
MISSING_BLOCKING = "MISSING_BLOCKING"


@dataclass(frozen=True)
class CompatibilityFieldStatus:
    legacy_field: str
    source_field: str | None
    status: str
    value_origin: str
    transformation: str | None
    business_effect: str
    handoff_permitted: bool


@dataclass(frozen=True)
class CompatibilityResult:
    compatible: bool
    dataframe: pd.DataFrame | None
    manifest_version: str
    manifest: tuple[CompatibilityFieldStatus, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    selected_rfq_number: str | None
    selected_rfq_item: str | None
    workbook_comparison_currency: str | None


def _decimal(value: Any) -> Decimal | None:
    try:
        if value is None or str(value).strip() == "":
            return None
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None


def _selected_quotes(orchestration_result: Any, rfq_number: str, rfq_item: str) -> list[Any]:
    return [
        item for item in orchestration_result.enriched_quotes
        if str(item.record.canonical_values.get("RFQ_NUMBER")) == str(rfq_number)
        and str(item.record.canonical_values.get("RFQ_ITEM")) == str(rfq_item)
    ]


def assess_legacy_compatibility(
    orchestration_result: Any,
    *,
    selected_rfq_number: str | None,
    selected_rfq_item: str | None,
) -> CompatibilityResult:
    """Return an auditable review-only compatibility report.

    No DataFrame is ever produced. Original ignored columns remain provenance-only.
    """
    blockers = [GOVERNED_RANKING_INPUTS_NOT_CANONICAL]
    manifest: list[CompatibilityFieldStatus] = [
        CompatibilityFieldStatus(
            "Frozen engine ranking inputs",
            None,
            MISSING_BLOCKING,
            "CANONICAL_SCHEMA_GAP",
            None,
            "A future Build B/C canonical contract extension is required before governed analytical handoff.",
            False,
        )
    ]
    quotes = _selected_quotes(
        orchestration_result,
        str(selected_rfq_number or ""),
        str(selected_rfq_item or ""),
    )
    if not selected_rfq_number or not selected_rfq_item:
        blockers.append("RFQ_ITEM_SELECTION_REQUIRED")
    if len([item for item in quotes if item.eligible_for_analysis]) < 2:
        blockers.append("MINIMUM_ELIGIBLE_SUPPLIER_COUNT_NOT_MET")

    currencies = {
        str(item.normalization.normalized_values.get("COMPARISON_CURRENCY") or "").upper()
        for item in quotes
    }
    workbook_currency = next(iter(currencies), None) if len(currencies) == 1 else None
    if len(currencies) != 1 or not workbook_currency:
        blockers.append("ONE_WORKBOOK_COMPARISON_CURRENCY_REQUIRED")

    for item in quotes:
        normalized = item.normalization.normalized_values
        row_id = item.record.provenance.source_row_id
        manifest.extend((
            CompatibilityFieldStatus("Source Currency", "SOURCE_CURRENCY", SUPPLIED, "SOURCE_WORKBOOK", None, f"Preserved for {row_id}.", False),
            CompatibilityFieldStatus("Source Price", "SOURCE_PRICE", SUPPLIED, "SOURCE_WORKBOOK", None, f"Preserved for {row_id}.", False),
            CompatibilityFieldStatus("Workbook Comparison Currency", "COMPARISON_CURRENCY", DERIVED, "BUILD_D_NORMALIZATION", None, f"Review basis for {row_id}.", False),
            CompatibilityFieldStatus("Normalized Unit Price", "NORMALIZED_UNIT_PRICE", DERIVED, "BUILD_D_NORMALIZATION", None, f"Review-only normalized value for {row_id}.", False),
            CompatibilityFieldStatus("Original ignored columns", None, EXCLUDED, "PROVENANCE_ONLY", None, f"Never used analytically for {row_id}.", False),
        ))
        if _decimal(normalized.get("NORMALIZED_UNIT_PRICE")) is None:
            blockers.append(f"NORMALIZED_REVIEW_VALUE_MISSING:{row_id}")

    return CompatibilityResult(
        compatible=False,
        dataframe=None,
        manifest_version=MANIFEST_VERSION,
        manifest=tuple(manifest),
        blockers=tuple(dict.fromkeys(blockers)),
        warnings=(REVIEW_ONLY,),
        selected_rfq_number=selected_rfq_number,
        selected_rfq_item=selected_rfq_item,
        workbook_comparison_currency=workbook_currency,
    )


def display_currency_frame(dataframe: pd.DataFrame, mode: str, fx_rate: float | int | Decimal | None) -> pd.DataFrame:
    """Return a display-only copy; never mutate review or engine values."""
    normalized_mode = str(mode or "USD").strip().upper()
    if normalized_mode not in {"USD", "INR", "BOTH"}:
        raise ValueError("DISPLAY_CURRENCY_UNSUPPORTED")
    result = dataframe.copy(deep=True)
    if normalized_mode == "USD":
        return result
    rate = _decimal(fx_rate)
    if rate is None or rate <= 0:
        raise ValueError("DISPLAY_FX_RATE_REQUIRED")
    if "Quoted Unit Price USD" not in result:
        raise ValueError("DISPLAY_CONVERSION_FAILED")
    usd = pd.to_numeric(result["Quoted Unit Price USD"], errors="coerce")
    if usd.isna().any():
        raise ValueError("DISPLAY_CONVERSION_FAILED")
    result["Quoted Unit Price INR"] = usd * float(rate)
    return result
