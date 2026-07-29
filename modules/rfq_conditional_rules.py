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

def resolve_evaluation_date(metadata: Mapping[str, Any] | None, records: Iterable[Any], explicit: date | None = None, today: date | None = None):
    if explicit: return explicit, "EXPLICIT_INPUT", ()
    metadata = metadata or {}
    for field in ("UPLOAD_CREATED_AT", "EXTRACTED_AT"):
        value = metadata.get(field)
        if isinstance(value, datetime): return value.date(), field, ()
        if isinstance(value, date): return value, field, ()
    candidates=[]
    for record in records:
        value=getattr(record,"canonical_values",{}).get("SOURCE_EXTRACTED_AT")
        if isinstance(value,datetime): candidates.append(value.date())
        elif isinstance(value,date): candidates.append(value)
    if candidates: return max(candidates), "LATEST_SOURCE_EXTRACTED_AT", ()
    return today or date.today(), "SYSTEM_DATE", (RuleFinding("Warning","SYSTEM_DATE_FALLBACK","System date used because no governed evaluation date was available."),)

def evaluate_conditional_rules(adapter_result: Any, evaluation_date: date, *, approved_free_text_row_ids: set[str] | None = None, history_staleness_days: int = 60):
    approved_free_text_row_ids=approved_free_text_row_ids or set(); findings=[]; quote_flags={}; history_flags={}; metadata=adapter_result.upload_metadata or {}
    if adapter_result.mode=="FULL_SOURCING_REVIEW":
        for field in ("HISTORY_START_DATE","HISTORY_END_DATE","HISTORY_SOURCE_TRANSACTION"):
            if not metadata.get(field): findings.append(RuleFinding("Blocking","FULL_REVIEW_HISTORY_METADATA_REQUIRED",f"{field} is required for FULL_SOURCING_REVIEW."))
        start,end=metadata.get("HISTORY_START_DATE"),metadata.get("HISTORY_END_DATE")
        if start and end and start>end: findings.append(RuleFinding("Fatal","HISTORY_WINDOW_INVALID","HISTORY_START_DATE must not be after HISTORY_END_DATE."))
        if not adapter_result.po_history: findings.append(RuleFinding("Warning","FULL_REVIEW_HISTORY_EMPTY","No PO history rows are available."))
    for record in adapter_result.rfq_quotes:
        v=record.canonical_values; row_id=record.provenance.source_row_id; eligible=bool(getattr(record,"eligible_for_analysis",getattr(record,"valid_for_analysis",True)))
        if not v.get("MATERIAL_ID") and row_id not in approved_free_text_row_ids: findings.append(RuleFinding("Blocking","MATERIAL_ID_REQUIRED","MATERIAL_ID is required unless explicitly approved as free text.",row_id)); eligible=False
        validity=v.get("VALIDITY_END_DATE")
        if isinstance(validity,date) and validity<evaluation_date: findings.append(RuleFinding("Blocking","QUOTATION_EXPIRED","Quotation is expired for the resolved evaluation date.",row_id)); eligible=False
        quote_flags[row_id]=eligible
    latest=None; start,end=metadata.get("HISTORY_START_DATE"),metadata.get("HISTORY_END_DATE")
    for record in adapter_result.po_history:
        v=record.canonical_values; row_id=record.provenance.source_row_id; eligible=bool(getattr(record,"row_valid",getattr(record,"valid_for_analysis",True))); po_date=v.get("PO_DATE")
        if start and isinstance(po_date,date) and po_date<start: eligible=False; findings.append(RuleFinding("Warning","HISTORY_ROW_OUT_OF_WINDOW","PO row is before HISTORY_START_DATE.",row_id))
        if end and isinstance(po_date,date) and po_date>end: eligible=False; findings.append(RuleFinding("Warning","HISTORY_ROW_OUT_OF_WINDOW","PO row is after HISTORY_END_DATE.",row_id))
        extracted=v.get("SOURCE_EXTRACTED_AT"); extracted=extracted.date() if isinstance(extracted,datetime) else extracted if isinstance(extracted,date) else None
        if extracted and (latest is None or extracted>latest): latest=extracted
        history_flags[row_id]=eligible
    if latest and (evaluation_date-latest).days>history_staleness_days: findings.append(RuleFinding("Warning","HISTORY_STALE",f"Latest eligible history evidence is older than {history_staleness_days} days."))
    return quote_flags,history_flags,tuple(findings)
