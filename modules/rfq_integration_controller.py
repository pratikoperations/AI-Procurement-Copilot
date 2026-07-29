"""Application integration controller for governed v1.3 workbook review."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from hashlib import sha256
import os
from typing import Any, Iterable, Mapping, MutableMapping

import pandas as pd

from modules.rfq_legacy_compatibility import CompatibilityResult, assess_legacy_compatibility
from modules.rfq_orchestration import OrchestrationResult, orchestrate_adapter_result
from modules.rfq_review_state import ReviewState, classify_orchestration_state, warning_controls
from modules.rfq_workbook_adapter import AdapterResult, WorkbookAdapterError, adapt_v13_workbook

ROUTE_FLAG = "AIPC_GOVERNED_V13_ROUTE_ENABLED"
ENABLED_VALUES = {"1", "true", "yes", "on"}
DISABLED_VALUES = {"", "0", "false", "no", "off"}
SESSION_UPLOAD_HASH_KEY = "governed_v13_active_upload_hash"
SESSION_REVIEW_KEYS = (
    "governed_v13_confirmed_mappings",
    "governed_v13_selected_event",
    "governed_v13_selected_rfq_number",
    "governed_v13_selected_rfq_item",
    "governed_v13_acknowledged_warnings",
    "governed_v13_handoff_digest",
)


@dataclass(frozen=True)
class ApplicationDataResult:
    route: str
    review_state: ReviewState
    dataframe: pd.DataFrame | None
    analysis_handoff_allowed: bool
    handoff_confirmed: bool
    stop_reason: str | None
    source_label: str
    adapter_result: AdapterResult | None
    orchestration_result: OrchestrationResult | None
    compatibility_result: CompatibilityResult | None
    findings: tuple[Any, ...]
    compatibility_manifest: tuple[Any, ...]
    route_warning: str | None = None


def governed_route_enabled(env: Mapping[str, str] | None = None) -> tuple[bool, str | None]:
    source = os.environ if env is None else env
    raw = str(source.get(ROUTE_FLAG, "")).strip().casefold()
    if raw in ENABLED_VALUES:
        return True, None
    if raw in DISABLED_VALUES:
        return False, None
    return False, f"Malformed {ROUTE_FLAG} value; governed route disabled."


def source_bytes(source: Any | None) -> bytes | None:
    if source is None:
        return None
    if isinstance(source, bytes):
        return source
    if isinstance(source, bytearray):
        return bytes(source)
    if hasattr(source, "getvalue"):
        value = source.getvalue()
        return value if isinstance(value, bytes) else bytes(value)
    return None


def upload_sha256(source: Any | None) -> str | None:
    payload = source_bytes(source)
    return None if payload is None else sha256(payload).hexdigest()


def reset_session_for_upload(session_state: MutableMapping[str, Any], source: Any | None) -> bool:
    """Clear prior governed decisions when uploaded workbook bytes change."""
    current = upload_sha256(source)
    previous = session_state.get(SESSION_UPLOAD_HASH_KEY)
    if current == previous:
        return False
    for key in SESSION_REVIEW_KEYS:
        session_state.pop(key, None)
    if current is None:
        session_state.pop(SESSION_UPLOAD_HASH_KEY, None)
    else:
        session_state[SESSION_UPLOAD_HASH_KEY] = current
    return True


def stopped_result(state: ReviewState, reason: str, *, route_warning: str | None = None, adapter_result: AdapterResult | None = None, orchestration_result: OrchestrationResult | None = None, compatibility_result: CompatibilityResult | None = None) -> ApplicationDataResult:
    findings = tuple(adapter_result.findings if adapter_result else ()) + tuple(orchestration_result.conditional_findings if orchestration_result else ())
    return ApplicationDataResult(
        route="GOVERNED_V13",
        review_state=state,
        dataframe=None,
        analysis_handoff_allowed=False,
        handoff_confirmed=False,
        stop_reason=reason,
        source_label="Governed v1.3 workbook review preview",
        adapter_result=adapter_result,
        orchestration_result=orchestration_result,
        compatibility_result=compatibility_result,
        findings=findings,
        compatibility_manifest=tuple(compatibility_result.manifest if compatibility_result else ()),
        route_warning=route_warning,
    )


def _item_keys(orchestration_result: OrchestrationResult) -> tuple[tuple[str, str], ...]:
    keys = {
        (str(item.record.canonical_values.get("RFQ_NUMBER") or ""), str(item.record.canonical_values.get("RFQ_ITEM") or ""))
        for item in orchestration_result.enriched_quotes if item.eligible_for_analysis
    }
    return tuple(sorted(key for key in keys if all(key)))


def run_governed_review(
    source: Any | None,
    *,
    filename: str | None = None,
    selected_sourcing_event_id: str | None = None,
    selected_rfq_number: str | None = None,
    selected_rfq_item: str | None = None,
    confirmed_mappings: Iterable[tuple[str, str, str]] = (),
    approved_free_text_row_ids: set[str] | None = None,
    approved_history_mappings: Mapping[str, str] | None = None,
    manual_history_confirmations: set[tuple[str, str]] | None = None,
    acknowledged_warning_codes: Iterable[str] = (),
    evaluation_date: date | None = None,
    comparison_currency: str | None = None,
    display_currency_mode: str = "USD",
    handoff_confirmation_digest: str | None = None,
    env: Mapping[str, str] | None = None,
    session_state: MutableMapping[str, Any] | None = None,
) -> ApplicationDataResult:
    """Run governed intake to a review-only terminal state."""
    del display_currency_mode, handoff_confirmation_digest
    enabled, route_warning = governed_route_enabled(env)
    if not enabled:
        return stopped_result(ReviewState.ROUTE_DISABLED, "Governed v1.3 route is disabled.", route_warning=route_warning)
    if source is None:
        return stopped_result(ReviewState.NO_FILE, "Upload a governed v1.3 workbook.")

    if session_state is None:
        try:
            import streamlit as st
            session_state = st.session_state
        except Exception:
            session_state = None
    if session_state is not None and reset_session_for_upload(session_state, source):
        selected_sourcing_event_id = None
        selected_rfq_number = None
        selected_rfq_item = None
        confirmed_mappings = ()
        acknowledged_warning_codes = ()

    approved_history_mappings = approved_history_mappings or {}
    manual_history_confirmations = manual_history_confirmations or set()
    confirmed_mappings = tuple(confirmed_mappings)
    try:
        adapter_result = adapt_v13_workbook(source, filename=filename, selected_sourcing_event_id=selected_sourcing_event_id, confirmed_mappings=confirmed_mappings)
    except WorkbookAdapterError as exc:
        return stopped_result(ReviewState.ADAPTER_FATAL, str(exc))

    if any(finding.severity == "Fatal" for finding in adapter_result.findings):
        return stopped_result(ReviewState.ADAPTER_FATAL, "Fatal workbook findings must be corrected.", adapter_result=adapter_result)
    if any(item.requires_confirmation for item in adapter_result.mapping_reviews):
        return stopped_result(ReviewState.MAPPING_CONFIRMATION_REQUIRED, "Confirm all high-risk normalized mappings.", adapter_result=adapter_result)
    if len(adapter_result.available_sourcing_event_ids) > 1 and not selected_sourcing_event_id:
        return stopped_result(ReviewState.EVENT_SELECTION_REQUIRED, "Select one sourcing event.", adapter_result=adapter_result)

    orchestration_result = orchestrate_adapter_result(
        adapter_result,
        evaluation_date=evaluation_date,
        comparison_currency=comparison_currency,
        approved_free_text_row_ids=approved_free_text_row_ids,
        approved_history_mappings=approved_history_mappings,
        manual_history_confirmations=manual_history_confirmations,
    )
    state = classify_orchestration_state(orchestration_result.eligibility_status)
    if state in {ReviewState.ORCHESTRATION_BLOCKED, ReviewState.INSUFFICIENT_EVIDENCE}:
        return stopped_result(state, orchestration_result.eligibility_status, adapter_result=adapter_result, orchestration_result=orchestration_result)

    if not selected_rfq_number or not selected_rfq_item:
        return stopped_result(ReviewState.ITEM_SELECTION_REQUIRED, "Select one RFQ item.", adapter_result=adapter_result, orchestration_result=orchestration_result)
    if (str(selected_rfq_number), str(selected_rfq_item)) not in _item_keys(orchestration_result):
        return stopped_result(ReviewState.ITEM_SELECTION_REQUIRED, "Selected RFQ item is not eligible.", adapter_result=adapter_result, orchestration_result=orchestration_result)

    blocking, outstanding = warning_controls(orchestration_result.warnings, adapter_result.mode, acknowledged_warning_codes)
    if outstanding:
        return stopped_result(ReviewState.CONDITIONAL_REVIEW_REQUIRED, "Acknowledge governed warning findings.", adapter_result=adapter_result, orchestration_result=orchestration_result)

    compatibility = assess_legacy_compatibility(orchestration_result, selected_rfq_number=str(selected_rfq_number), selected_rfq_item=str(selected_rfq_item))
    reason = "Governed review complete. Analytical handoff is disabled until ranking inputs are canonicalized."
    if blocking:
        reason = "Governed review complete with compatibility-blocking findings. Analytical handoff remains disabled."
    return stopped_result(ReviewState.REVIEW_ONLY_COMPLETE, reason, adapter_result=adapter_result, orchestration_result=orchestration_result, compatibility_result=compatibility)
