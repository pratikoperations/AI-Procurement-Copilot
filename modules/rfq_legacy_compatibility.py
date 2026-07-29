"""Build Group E bridge from governed RFQ evidence to the frozen legacy DataFrame contract."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Iterable, Mapping, Sequence

import pandas as pd

MANIFEST_VERSION = "AIPC-LEGACY-COMPATIBILITY-MANIFEST-1.3.0"
CANONICAL_ENGINE_CURRENCY = "USD"

SUPPLIED = "SUPPLIED"
DERIVED = "DERIVED"
DEFAULTED_BY_EXISTING_ENGINE = "DEFAULTED_BY_EXISTING_ENGINE"
EXCLUDED = "EXCLUDED"
MISSING_BLOCKING = "MISSING_BLOCKING"
UNSUPPORTED = "UNSUPPORTED"

CRITICAL_FIELDS = {
    "Supplier": "SUPPLIER_NAME",
    "MOQ": "MINIMUM_ORDER_QUANTITY",
    "Lead Time Days": "LEAD_TIME_DAYS",
    "Payment Terms": "PAYMENT_TERMS_CODE",
    "Incoterms": "INCOTERMS_CODE",
}

# Existing engines materially use or default these values. Initial governed
# handoff is fail-closed until every value is explicitly available.
RANKING_SENSITIVE_FIELDS = (
    "OTIF %",
    "Quality PPM",
    "Audit Score",
    "Complaint Rate %",
    "Capacity Buffer %",
    "Recyclability",
    "Certification",
    "Carbon Score",
    "EPR Readiness",
    "PCR Content %",
)


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
    canonical_engine_currency: str


def _decimal(value: Any) -> Decimal | None:
    try:
        if value is None or str(value).strip() == "":
            return None
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None


def _active_selected_quotes(orchestration_result: Any, rfq_number: str, rfq_item: str) -> list[Any]:
    return [
        item for item in orchestration_result.enriched_quotes
        if item.eligible_for_analysis
        and str(item.record.canonical_values.get("RFQ_NUMBER")) == str(rfq_number)
        and str(item.record.canonical_values.get("RFQ_ITEM")) == str(rfq_item)
    ]


def _manifest_entry(
    legacy_field: str,
    source_field: str | None,
    status: str,
    origin: str,
    effect: str,
    permitted: bool,
    transformation: str | None = None,
) -> CompatibilityFieldStatus:
    return CompatibilityFieldStatus(
        legacy_field,
        source_field,
        status,
        origin,
        transformation,
        effect,
        permitted,
    )


def assess_legacy_compatibility(
    orchestration_result: Any,
    *,
    selected_rfq_number: str | None,
    selected_rfq_item: str | None,
) -> CompatibilityResult:
    """Return a fail-closed, source-preserving compatibility assessment."""
    blockers: list[str] = []
    warnings: list[str] = []
    manifest: list[CompatibilityFieldStatus] = []

    if orchestration_result.eligibility_status in {"BLOCKED", "INSUFFICIENT_EVIDENCE"}:
        blockers.append(f"ORCHESTRATION_{orchestration_result.eligibility_status}")
    if not selected_rfq_number or not selected_rfq_item:
        blockers.append("RFQ_ITEM_SELECTION_REQUIRED")

    quotes = _active_selected_quotes(orchestration_result, str(selected_rfq_number or ""), str(selected_rfq_item or ""))
    if len(quotes) < 2:
        blockers.append("MINIMUM_ELIGIBLE_SUPPLIER_COUNT_NOT_MET")

    comparison_currencies = {
        str(item.normalization.normalized_values.get("COMPARISON_CURRENCY") or "").upper()
        for item in quotes
    }
    if comparison_currencies != {CANONICAL_ENGINE_CURRENCY}:
        blockers.append("CANONICAL_USD_ENGINE_VALUE_REQUIRED")

    comparison_uoms = {
        str(item.normalization.normalized_values.get("COMPARISON_UOM") or "").strip()
        for item in quotes
    }
    if len(comparison_uoms) != 1 or not next(iter(comparison_uoms), ""):
        blockers.append("ONE_COMPARISON_UOM_REQUIRED")

    rows: list[dict[str, Any]] = []
    for item in quotes:
        values = item.record.canonical_values
        normalized = item.normalization.normalized_values
        row_id = item.record.provenance.source_row_id
        row: dict[str, Any] = {}

        for legacy_field, source_field in CRITICAL_FIELDS.items():
            value = values.get(source_field)
            valid = value is not None and str(value).strip() != ""
            if legacy_field == "MOQ":
                valid = (_decimal(value) or Decimal("0")) > 0
            elif legacy_field == "Lead Time Days":
                numeric = _decimal(value)
                valid = numeric is not None and numeric >= 0
            if not valid:
                blockers.append(f"MISSING_COMPATIBILITY_FIELD:{row_id}:{source_field}")
                manifest.append(_manifest_entry(legacy_field, source_field, MISSING_BLOCKING, "SOURCE_WORKBOOK", "Required by frozen legacy analytical contract.", False))
            else:
                row[legacy_field] = value
                manifest.append(_manifest_entry(legacy_field, source_field, SUPPLIED, "SOURCE_WORKBOOK", "Direct governed field mapping.", True))

        price = _decimal(normalized.get("NORMALIZED_UNIT_PRICE"))
        if price is None or price <= 0 or str(normalized.get("COMPARISON_CURRENCY") or "").upper() != CANONICAL_ENGINE_CURRENCY:
            blockers.append(f"CANONICAL_USD_PRICE_INVALID:{row_id}")
            manifest.append(_manifest_entry("Quoted Unit Price USD", "NORMALIZED_UNIT_PRICE", MISSING_BLOCKING, "BUILD_D_NORMALIZATION", "Positive canonical USD price is mandatory.", False))
        else:
            row["Quoted Unit Price USD"] = float(price)
            row["Currency"] = CANONICAL_ENGINE_CURRENCY
            row["Original Currency"] = normalized.get("SOURCE_CURRENCY")
            row["Original Unit Price"] = normalized.get("SOURCE_PRICE")
            row["Normalized Currency"] = CANONICAL_ENGINE_CURRENCY
            row["Normalized Unit Price"] = float(price)
            row["FX Rate Used"] = normalized.get("EXCHANGE_RATE_USED")
            row["FX Rate Date"] = normalized.get("EXCHANGE_RATE_DATE_USED")
            row["Unit"] = normalized.get("COMPARISON_UOM")
            row["Unit of Measure"] = normalized.get("COMPARISON_UOM")
            row["Comparison Basis"] = f"USD per {normalized.get('COMPARISON_UOM')}"
            manifest.extend((
                _manifest_entry("Quoted Unit Price USD", "NORMALIZED_UNIT_PRICE", DERIVED, "BUILD_D_NORMALIZATION", "Canonical engine price; no second normalization.", True),
                _manifest_entry("Currency", "COMPARISON_CURRENCY", DERIVED, "ENGINE_CANONICAL", "Frozen engine currency label.", True),
                _manifest_entry("Original Currency", "SOURCE_CURRENCY", SUPPLIED, "SOURCE_WORKBOOK", "Source currency preserved.", True),
                _manifest_entry("Original Unit Price", "SOURCE_PRICE", SUPPLIED, "SOURCE_WORKBOOK", "Source price preserved.", True),
                _manifest_entry("FX Rate Used", "EXCHANGE_RATE_USED", DERIVED, "BUILD_D_NORMALIZATION", "Governed normalization evidence.", True),
                _manifest_entry("FX Rate Date", "EXCHANGE_RATE_DATE_USED", SUPPLIED, "SOURCE_WORKBOOK", "Governed FX evidence date.", True),
            ))

        row["Material"] = values.get("MATERIAL_DESCRIPTION")
        row["Plant"] = values.get("PLANT")
        row["RFQ Number"] = values.get("RFQ_NUMBER")
        row["RFQ Item"] = values.get("RFQ_ITEM")
        row["Source Row ID"] = row_id

        original = item.record.original_values
        for field in RANKING_SENSITIVE_FIELDS:
            value = original.get(field) if isinstance(original, Mapping) else None
            if value is None or str(value).strip() == "":
                blockers.append(f"RANKING_INPUT_MISSING:{row_id}:{field}")
                manifest.append(_manifest_entry(field, None, MISSING_BLOCKING, "UNAVAILABLE", "Existing engine would otherwise apply a ranking-sensitive default.", False))
            else:
                row[field] = value
                manifest.append(_manifest_entry(field, field, SUPPLIED, "SOURCE_WORKBOOK", "Explicit legacy-compatible ranking input.", True))
        rows.append(row)

    unique_blockers = tuple(dict.fromkeys(blockers))
    compatible = bool(rows) and not unique_blockers
    dataframe = pd.DataFrame(rows) if compatible else None
    if dataframe is not None:
        dataframe.attrs["source_label"] = "Governed v1.3 workbook — human-reviewed compatibility handoff"
        dataframe.attrs["build_e_canonical_engine_currency"] = CANONICAL_ENGINE_CURRENCY
        dataframe.attrs["build_e_manifest_version"] = MANIFEST_VERSION
        dataframe.attrs["build_e_no_legacy_currency_normalization"] = True

    return CompatibilityResult(
        compatible,
        dataframe,
        MANIFEST_VERSION,
        tuple(manifest),
        unique_blockers,
        tuple(dict.fromkeys(warnings)),
        selected_rfq_number,
        selected_rfq_item,
        CANONICAL_ENGINE_CURRENCY,
    )


def display_currency_frame(dataframe: pd.DataFrame, mode: str, fx_rate: float | int | Decimal | None) -> pd.DataFrame:
    """Return a display-only copy; never mutate canonical engine values."""
    normalized_mode = str(mode or "USD").strip().upper()
    if normalized_mode not in {"USD", "INR", "BOTH"}:
        raise ValueError("DISPLAY_CURRENCY_UNSUPPORTED")
    result = dataframe.copy(deep=True)
    if normalized_mode == "USD":
        return result
    rate = _decimal(fx_rate)
    if rate is None or rate <= 0:
        raise ValueError("DISPLAY_FX_RATE_REQUIRED")
    usd = pd.to_numeric(result["Quoted Unit Price USD"], errors="coerce")
    if usd.isna().any():
        raise ValueError("DISPLAY_CONVERSION_FAILED")
    if normalized_mode == "INR":
        result["Quoted Unit Price INR"] = usd * float(rate)
    else:
        result["Quoted Unit Price INR"] = usd * float(rate)
    return result
