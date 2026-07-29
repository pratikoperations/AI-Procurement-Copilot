"""Conditional contract rules for v1.3 orchestration."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Iterable, Mapping


@dataclass(frozen=True)
class RuleFinding:
    severity: str
    code: str
    message: str
    source_row_id: str | None = None


def _as_date(value: Any) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return None


def resolve_evaluation_date(metadata: Mapping[str, Any] | None, records: Iterable[Any], explicit: date | None = None, today: date | None = None):
    if explicit:
        return explicit, "EXPLICIT_INPUT", ()
    metadata = metadata or {}
    for field in ("UPLOAD_CREATED_AT", "EXTRACTED_AT"):
        resolved = _as_date(metadata.get(field))
        if resolved:
            return resolved, field, ()
    candidates = [resolved for record in records if (resolved := _as_date(getattr(record, "canonical_values", {}).get("SOURCE_EXTRACTED_AT")))]
    if candidates:
        return max(candidates), "LATEST_SOURCE_EXTRACTED_AT", ()
    return today or date.today(), "SYSTEM_DATE", (
        RuleFinding("Warning", "SYSTEM_DATE_FALLBACK", "System date used because no governed evaluation date was available."),
    )


def evaluate_conditional_rules(adapter_result: Any, evaluation_date: date, *, approved_free_text_row_ids: set[str] | None = None):
    approved_free_text_row_ids = approved_free_text_row_ids or set()
    findings: list[RuleFinding] = []
    quote_flags: dict[str, bool] = {}
    history_flags: dict[str, bool] = {}
    metadata = adapter_result.upload_metadata or {}
    start = _as_date(metadata.get("HISTORY_START_DATE"))
    end = _as_date(metadata.get("HISTORY_END_DATE"))

    if adapter_result.mode == "FULL_SOURCING_REVIEW":
        for field in ("HISTORY_START_DATE", "HISTORY_END_DATE", "HISTORY_SOURCE_TRANSACTION"):
            if not metadata.get(field):
                findings.append(RuleFinding("Blocking", "FULL_REVIEW_HISTORY_METADATA_REQUIRED", f"{field} is required for FULL_SOURCING_REVIEW."))
        if start and end and start > end:
            findings.append(RuleFinding("Fatal", "HISTORY_WINDOW_INVALID", "HISTORY_START_DATE must not be after HISTORY_END_DATE."))
        if not adapter_result.po_history:
            findings.append(RuleFinding("Warning", "FULL_REVIEW_HISTORY_EMPTY", "No PO history rows are available."))

    for record in adapter_result.rfq_quotes:
        values = record.canonical_values
        row_id = record.provenance.source_row_id
        eligible = bool(getattr(record, "eligible_for_analysis", getattr(record, "valid_for_analysis", True)))
        if not values.get("MATERIAL_ID") and row_id not in approved_free_text_row_ids:
            findings.append(RuleFinding("Blocking", "MATERIAL_ID_REQUIRED", "MATERIAL_ID is required unless explicitly approved as free text.", row_id))
            eligible = False
        validity = _as_date(values.get("VALIDITY_END_DATE"))
        if validity and validity < evaluation_date:
            findings.append(RuleFinding("Blocking", "QUOTATION_EXPIRED", "Quotation is expired for the resolved evaluation date.", row_id))
            eligible = False
        quote_flags[row_id] = eligible

    for record in adapter_result.po_history:
        values = record.canonical_values
        row_id = record.provenance.source_row_id
        eligible = bool(getattr(record, "row_valid", getattr(record, "valid_for_analysis", True)))
        po_date = _as_date(values.get("PO_DATE"))
        if start and po_date and po_date < start:
            eligible = False
            findings.append(RuleFinding("Warning", "HISTORY_ROW_OUT_OF_WINDOW", "PO row is before HISTORY_START_DATE.", row_id))
        if end and po_date and po_date > end:
            eligible = False
            findings.append(RuleFinding("Warning", "HISTORY_ROW_OUT_OF_WINDOW", "PO row is after HISTORY_END_DATE.", row_id))
        history_flags[row_id] = eligible

    return quote_flags, history_flags, tuple(findings)


def evaluate_history_staleness(history_records: Iterable[Any], eligible_row_ids: set[str], evaluation_date: date, *, history_staleness_days: int = 60):
    current_ids: set[str] = set()
    stale_ids: list[str] = []
    for record in history_records:
        row_id = record.provenance.source_row_id
        if row_id not in eligible_row_ids:
            continue
        extracted = _as_date(record.canonical_values.get("SOURCE_EXTRACTED_AT"))
        if extracted is None:
            continue
        if (evaluation_date - extracted).days <= history_staleness_days:
            current_ids.add(row_id)
        else:
            stale_ids.append(row_id)
    findings = ()
    if stale_ids:
        findings = (
            RuleFinding("Warning", "HISTORY_STALE", f"History rows older than {history_staleness_days} days were excluded: {', '.join(sorted(stale_ids))}."),
        )
    return current_ids, findings
