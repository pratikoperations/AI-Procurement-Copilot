"""Application integration controller for governed v1.3 review and E2 handoff.

Review-only compatibility contract:
dataframe=None
analysis_handoff_allowed=False
handoff_confirmed=False
until exact E2 digest confirmation.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from hashlib import sha256
import os
from typing import Any, Iterable, Mapping, MutableMapping

import pandas as pd

from modules.rfq_analytical_handoff import build_analytical_handoff
from modules.rfq_handoff_models import AnalyticalHandoffResult
from modules.rfq_legacy_compatibility import CompatibilityResult, assess_legacy_compatibility
from modules.rfq_orchestration import OrchestrationResult, orchestrate_adapter_result
from modules.rfq_review_state import ReviewState, classify_orchestration_state, stable_digest, warning_controls
from modules.rfq_workbook_adapter import AdapterResult, RankingMappingConfirmation, WorkbookAdapterError, adapt_v13_workbook

ROUTE_FLAG = "AIPC_GOVERNED_V13_ROUTE_ENABLED"
HANDOFF_FLAG = "AIPC_GOVERNED_V13_ANALYTICAL_HANDOFF_ENABLED"
ENABLED_VALUES = {"1", "true", "yes", "on"}
DISABLED_VALUES = {"", "0", "false", "no", "off"}
SESSION_UPLOAD_HASH_KEY = "governed_v13_active_upload_hash"
SESSION_REVIEW_KEYS = (
    "governed_v13_confirmed_mappings",
    "governed_v13_ranking_confirmations",
    "governed_v13_selected_event",
    "governed_v13_selected_rfq_number",
    "governed_v13_selected_rfq_item",
    "governed_v13_acknowledged_warnings",
    "governed_v13_handoff_digest",
    "governed_v13_handoff_manifest_digest",
    "governed_v13_handoff_confirmed_at",
    "governed_v13_handoff_contract_version",
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
    handoff_result: AnalyticalHandoffResult | None = None
    handoff_digest: str | None = None


def _flag(name: str, env: Mapping[str, str] | None = None) -> tuple[bool, str | None]:
    source = os.environ if env is None else env
    raw = str(source.get(name, "")).strip().casefold()
    if raw in ENABLED_VALUES:
        return True, None
    if raw in DISABLED_VALUES:
        return False, None
    return False, f"Malformed {name} value; capability disabled."


def governed_route_enabled(env: Mapping[str, str] | None = None) -> tuple[bool, str | None]:
    return _flag(ROUTE_FLAG, env)


def analytical_handoff_enabled(env: Mapping[str, str] | None = None) -> tuple[bool, str | None]:
    return _flag(HANDOFF_FLAG, env)


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


def stopped_result(state: ReviewState, reason: str, *, route_warning: str | None = None, adapter_result: AdapterResult | None = None, orchestration_result: OrchestrationResult | None = None, compatibility_result: CompatibilityResult | None = None, handoff_result: AnalyticalHandoffResult | None = None) -> ApplicationDataResult:
    findings = tuple(adapter_result.findings if adapter_result else ()) + tuple(orchestration_result.conditional_findings if orchestration_result else ()) + tuple(handoff_result.findings if handoff_result else ())
    return ApplicationDataResult("GOVERNED_V13", state, None, False, False, reason, "Governed v1.3 workbook review", adapter_result, orchestration_result, compatibility_result, findings, tuple(compatibility_result.manifest if compatibility_result else ()), route_warning, handoff_result, None if handoff_result is None else handoff_result.digest)


def _item_keys(orchestration_result: OrchestrationResult) -> tuple[tuple[str, str], ...]:
    keys = {(str(item.record.canonical_values.get("RFQ_NUMBER") or ""), str(item.record.canonical_values.get("RFQ_ITEM") or "")) for item in orchestration_result.enriched_quotes if item.eligible_for_analysis}
    return tuple(sorted(key for key in keys if all(key)))


def run_governed_review(
    source: Any | None,
    *,
    filename: str | None = None,
    selected_sourcing_event_id: str | None = None,
    selected_rfq_number: str | None = None,
    selected_rfq_item: str | None = None,
    confirmed_mappings: Iterable[tuple[str, str, str]] = (),
    ranking_confirmations: Iterable[RankingMappingConfirmation] = (),
    approved_free_text_row_ids: set[str] | None = None,
    approved_history_mappings: Mapping[str, str] | None = None,
    manual_history_confirmations: set[tuple[str, str]] | None = None,
    acknowledged_warning_codes: Iterable[str] = (),
    evaluation_date: date | None = None,
    comparison_currency: str | None = None,
    display_currency_mode: str = "USD",
    handoff_confirmation_digest: str | None = None,
    analytical_assumptions: Mapping[str, Any] | None = None,
    env: Mapping[str, str] | None = None,
    session_state: MutableMapping[str, Any] | None = None,
) -> ApplicationDataResult:
    del display_currency_mode
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
        selected_sourcing_event_id = selected_rfq_number = selected_rfq_item = None
        confirmed_mappings = (); ranking_confirmations = (); acknowledged_warning_codes = (); handoff_confirmation_digest = None

    approved_history_mappings = approved_history_mappings or {}
    manual_history_confirmations = manual_history_confirmations or set()
    try:
        adapter_result = adapt_v13_workbook(source, filename=filename, selected_sourcing_event_id=selected_sourcing_event_id, confirmed_mappings=tuple(confirmed_mappings), ranking_confirmations=tuple(ranking_confirmations), evaluation_date=evaluation_date)
    except WorkbookAdapterError as exc:
        return stopped_result(ReviewState.ADAPTER_FATAL, str(exc))
    pending_mappings = tuple(item for item in adapter_result.mapping_reviews if item.requires_confirmation)
    if pending_mappings:
        return stopped_result(ReviewState.MAPPING_CONFIRMATION_REQUIRED, "Confirm all governed mappings.", adapter_result=adapter_result)
    if len(adapter_result.available_sourcing_event_ids) > 1 and not selected_sourcing_event_id:
        return stopped_result(ReviewState.EVENT_SELECTION_REQUIRED, "Select one sourcing event.", adapter_result=adapter_result)
    if any(finding.severity == "Fatal" for finding in adapter_result.findings):
        return stopped_result(ReviewState.ADAPTER_FATAL, "Fatal workbook findings must be corrected.", adapter_result=adapter_result)

    orchestration_result = orchestrate_adapter_result(adapter_result, evaluation_date=evaluation_date, comparison_currency=comparison_currency, approved_free_text_row_ids=approved_free_text_row_ids, approved_history_mappings=approved_history_mappings, manual_history_confirmations=manual_history_confirmations)
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

    handoff_flag, handoff_warning = analytical_handoff_enabled(env)
    if not handoff_flag:
        compatibility = assess_legacy_compatibility(orchestration_result, selected_rfq_number=str(selected_rfq_number), selected_rfq_item=str(selected_rfq_item))
        reason = handoff_warning or "Governed review complete. Analytical handoff feature is disabled."
        return stopped_result(ReviewState.REVIEW_ONLY_COMPLETE, reason, route_warning=handoff_warning, adapter_result=adapter_result, orchestration_result=orchestration_result, compatibility_result=compatibility)
    if blocking:
        compatibility = assess_legacy_compatibility(orchestration_result, selected_rfq_number=str(selected_rfq_number), selected_rfq_item=str(selected_rfq_item))
        return stopped_result(ReviewState.ANALYSIS_INCOMPATIBLE, "Compatibility-blocking warnings remain.", adapter_result=adapter_result, orchestration_result=orchestration_result, compatibility_result=compatibility)

    ranking_confirmations = tuple(ranking_confirmations)
    approvals = {
        "confirmed_mappings": stable_digest(tuple(confirmed_mappings)),
        "ranking_confirmations": stable_digest([item.__dict__ for item in ranking_confirmations]),
        "history_mappings": stable_digest(approved_history_mappings),
        "manual_history": stable_digest(tuple(sorted(manual_history_confirmations))),
        "warnings": stable_digest(tuple(sorted(acknowledged_warning_codes))),
    }
    handoff = build_analytical_handoff(adapter_result, orchestration_result, selected_sourcing_event_id=str(selected_sourcing_event_id or ""), selected_rfq_number=str(selected_rfq_number), selected_rfq_item=str(selected_rfq_item), evaluation_date=orchestration_result.evaluation_date, analytical_assumptions=analytical_assumptions or {}, approval_digests=approvals)
    confirmed = bool(handoff.eligible and handoff.digest and handoff_confirmation_digest == handoff.digest)
    compatibility = assess_legacy_compatibility(orchestration_result, selected_rfq_number=str(selected_rfq_number), selected_rfq_item=str(selected_rfq_item), handoff_result=handoff, handoff_confirmed=confirmed)
    if not handoff.eligible:
        return stopped_result(ReviewState.ANALYSIS_INCOMPATIBLE, "Selected item is not eligible for governed analytical handoff.", adapter_result=adapter_result, orchestration_result=orchestration_result, compatibility_result=compatibility, handoff_result=handoff)
    if not confirmed:
        return stopped_result(ReviewState.READY_FOR_HANDOFF, "Confirm the exact governed analytical handoff digest.", adapter_result=adapter_result, orchestration_result=orchestration_result, compatibility_result=compatibility, handoff_result=handoff)
    dataframe = compatibility.dataframe
    if dataframe is None:
        return stopped_result(ReviewState.ANALYSIS_INCOMPATIBLE, "Confirmed handoff did not produce a DataFrame.", adapter_result=adapter_result, orchestration_result=orchestration_result, compatibility_result=compatibility, handoff_result=handoff)
    findings = tuple(adapter_result.findings) + tuple(orchestration_result.conditional_findings) + tuple(handoff.findings)
    return ApplicationDataResult("GOVERNED_V13", ReviewState.HANDOFF_CONFIRMED, dataframe, True, True, None, "Governed v1.3 analytical handoff", adapter_result, orchestration_result, compatibility, findings, tuple(compatibility.manifest), None, handoff, handoff.digest)
