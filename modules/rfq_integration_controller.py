"""Application integration controller for governed v1.3 workbook review."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import os
from typing import Any, Iterable, Mapping

import pandas as pd

from modules.rfq_legacy_compatibility import CompatibilityResult, assess_legacy_compatibility
from modules.rfq_orchestration import OrchestrationResult, orchestrate_adapter_result
from modules.rfq_review_state import (
    ReviewIdentity,
    ReviewState,
    classify_orchestration_state,
    stable_digest,
    warning_controls,
)
from modules.rfq_workbook_adapter import AdapterResult, WorkbookAdapterError, adapt_v13_workbook

ROUTE_FLAG = "AIPC_GOVERNED_V13_ROUTE_ENABLED"
ENABLED_VALUES = {"1", "true", "yes", "on"}
DISABLED_VALUES = {"", "0", "false", "no", "off"}


@dataclass(frozen=True)
class ApplicationDataResult:
    route: str
    review_state: ReviewState
    dataframe: pd.DataFrame | None
    analysis_handoff_allowed: bool
    handoff_confirmed: bool
    stop_reason: str | None
    source_label: str
    review_identity: ReviewIdentity | None
    adapter_result: AdapterResult | None
    orchestration_result: OrchestrationResult | None
    compatibility_result: CompatibilityResult | None
    findings: tuple[Any, ...]
    compatibility_manifest: tuple[Any, ...]
    route_warning: str | None = None


def governed_route_enabled(env: Mapping[str, str] | None = None) -> tuple[bool, str | None]:
    """Read the route flag using a disabled-by-default, fail-closed policy."""
    source = os.environ if env is None else env
    raw = str(source.get(ROUTE_FLAG, "")).strip().casefold()
    if raw in ENABLED_VALUES:
        return True, None
    if raw in DISABLED_VALUES:
        return False, None
    return False, f"Malformed {ROUTE_FLAG} value; governed route disabled."


def _adapter_fatal(adapter_result: AdapterResult) -> bool:
    return any(finding.severity == "Fatal" for finding in adapter_result.findings)


def _pending_mapping_reviews(adapter_result: AdapterResult) -> tuple[Any, ...]:
    return tuple(item for item in adapter_result.mapping_reviews if item.requires_confirmation)


def _selected_item_keys(orchestration_result: OrchestrationResult) -> tuple[tuple[str, str], ...]:
    keys = {
        (
            str(item.record.canonical_values.get("RFQ_NUMBER") or ""),
            str(item.record.canonical_values.get("RFQ_ITEM") or ""),
        )
        for item in orchestration_result.enriched_quotes
        if item.eligible_for_analysis
    }
    return tuple(sorted(key for key in keys if all(key)))


def _build_identity(
    adapter_result: AdapterResult,
    orchestration_result: OrchestrationResult,
    compatibility_result: CompatibilityResult,
    *,
    selected_rfq_number: str,
    selected_rfq_item: str,
    display_currency_mode: str,
    confirmed_mappings: Iterable[tuple[str, str, str]],
    approved_history_mappings: Mapping[str, str],
    manual_history_confirmations: Iterable[tuple[str, str]],
) -> ReviewIdentity:
    return ReviewIdentity(
        upload_hash_sha256=adapter_result.upload_file_hash_sha256,
        schema_version=adapter_result.schema_version,
        alias_registry_version=adapter_result.alias_registry_version,
        selected_sourcing_event_id=str(adapter_result.selected_sourcing_event_id or ""),
        selected_rfq_number=str(selected_rfq_number),
        selected_rfq_item=str(selected_rfq_item),
        canonical_engine_currency=compatibility_result.canonical_engine_currency,
        display_currency_mode=str(display_currency_mode).upper(),
        evaluation_date=orchestration_result.evaluation_date,
        evaluation_date_source=orchestration_result.evaluation_date_source,
        adapter_finding_digest=stable_digest([item.__dict__ for item in adapter_result.findings]),
        orchestration_finding_digest=stable_digest([item.__dict__ for item in orchestration_result.conditional_findings]),
        compatibility_manifest_digest=stable_digest([item.__dict__ for item in compatibility_result.manifest]),
        approved_mapping_digest=stable_digest(sorted(tuple(item) for item in confirmed_mappings)),
        approved_history_mapping_digest=stable_digest(sorted(approved_history_mappings.items())),
        manual_history_confirmation_digest=stable_digest(sorted(tuple(item) for item in manual_history_confirmations)),
    )


def stopped_result(
    state: ReviewState,
    reason: str,
    *,
    route_warning: str | None = None,
    adapter_result: AdapterResult | None = None,
    orchestration_result: OrchestrationResult | None = None,
    compatibility_result: CompatibilityResult | None = None,
) -> ApplicationDataResult:
    findings = tuple(adapter_result.findings if adapter_result else ()) + tuple(orchestration_result.conditional_findings if orchestration_result else ())
    return ApplicationDataResult(
        route="GOVERNED_V13",
        review_state=state,
        dataframe=None,
        analysis_handoff_allowed=False,
        handoff_confirmed=False,
        stop_reason=reason,
        source_label="Governed v1.3 workbook review preview",
        review_identity=None,
        adapter_result=adapter_result,
        orchestration_result=orchestration_result,
        compatibility_result=compatibility_result,
        findings=findings,
        compatibility_manifest=tuple(compatibility_result.manifest if compatibility_result else ()),
        route_warning=route_warning,
    )


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
    comparison_currency: str = "USD",
    display_currency_mode: str = "USD",
    handoff_confirmation_digest: str | None = None,
    env: Mapping[str, str] | None = None,
) -> ApplicationDataResult:
    """Run governed intake and return either a stop state or confirmed DataFrame."""
    enabled, route_warning = governed_route_enabled(env)
    if not enabled:
        return stopped_result(ReviewState.ROUTE_DISABLED, "Governed v1.3 route is disabled.", route_warning=route_warning)
    if source is None:
        return stopped_result(ReviewState.NO_FILE, "Upload a governed v1.3 workbook.")

    approved_history_mappings = approved_history_mappings or {}
    manual_history_confirmations = manual_history_confirmations or set()
    confirmed_mappings = tuple(confirmed_mappings)
    try:
        adapter_result = adapt_v13_workbook(
            source,
            filename=filename,
            selected_sourcing_event_id=selected_sourcing_event_id,
            confirmed_mappings=confirmed_mappings,
        )
    except WorkbookAdapterError as exc:
        return stopped_result(ReviewState.ADAPTER_FATAL, str(exc))

    if _adapter_fatal(adapter_result):
        return stopped_result(ReviewState.ADAPTER_FATAL, "Fatal workbook findings must be corrected.", adapter_result=adapter_result)
    pending = _pending_mapping_reviews(adapter_result)
    if pending:
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
    orchestration_state = classify_orchestration_state(orchestration_result.eligibility_status)
    if orchestration_state in {ReviewState.ORCHESTRATION_BLOCKED, ReviewState.INSUFFICIENT_EVIDENCE}:
        return stopped_result(orchestration_state, orchestration_result.eligibility_status, adapter_result=adapter_result, orchestration_result=orchestration_result)

    item_keys = _selected_item_keys(orchestration_result)
    if not selected_rfq_number or not selected_rfq_item:
        return stopped_result(ReviewState.ITEM_SELECTION_REQUIRED, "Select one RFQ item.", adapter_result=adapter_result, orchestration_result=orchestration_result)
    if (str(selected_rfq_number), str(selected_rfq_item)) not in item_keys:
        return stopped_result(ReviewState.ITEM_SELECTION_REQUIRED, "Selected RFQ item is not eligible.", adapter_result=adapter_result, orchestration_result=orchestration_result)

    blocking_warnings, outstanding = warning_controls(
        orchestration_result.warnings,
        adapter_result.mode,
        acknowledged_warning_codes,
    )
    if blocking_warnings:
        return stopped_result(ReviewState.ANALYSIS_INCOMPATIBLE, "Compatibility-blocking warning findings remain.", adapter_result=adapter_result, orchestration_result=orchestration_result)
    if outstanding:
        return stopped_result(ReviewState.CONDITIONAL_REVIEW_REQUIRED, "Acknowledge governed warning findings.", adapter_result=adapter_result, orchestration_result=orchestration_result)

    compatibility = assess_legacy_compatibility(
        orchestration_result,
        selected_rfq_number=str(selected_rfq_number),
        selected_rfq_item=str(selected_rfq_item),
    )
    if not compatibility.compatible:
        return stopped_result(ReviewState.ANALYSIS_INCOMPATIBLE, "Legacy analytical compatibility requirements are not met.", adapter_result=adapter_result, orchestration_result=orchestration_result, compatibility_result=compatibility)

    identity = _build_identity(
        adapter_result,
        orchestration_result,
        compatibility,
        selected_rfq_number=str(selected_rfq_number),
        selected_rfq_item=str(selected_rfq_item),
        display_currency_mode=display_currency_mode,
        confirmed_mappings=confirmed_mappings,
        approved_history_mappings=approved_history_mappings,
        manual_history_confirmations=manual_history_confirmations,
    )
    confirmed = handoff_confirmation_digest == identity.digest
    if not confirmed:
        result = stopped_result(ReviewState.READY_FOR_HANDOFF, "Explicit human handoff confirmation is required.", adapter_result=adapter_result, orchestration_result=orchestration_result, compatibility_result=compatibility)
        return ApplicationDataResult(**{**result.__dict__, "review_identity": identity})

    return ApplicationDataResult(
        route="GOVERNED_V13",
        review_state=ReviewState.HANDOFF_CONFIRMED,
        dataframe=compatibility.dataframe,
        analysis_handoff_allowed=True,
        handoff_confirmed=True,
        stop_reason=None,
        source_label="Governed v1.3 workbook — human-reviewed analytical handoff",
        review_identity=identity,
        adapter_result=adapter_result,
        orchestration_result=orchestration_result,
        compatibility_result=compatibility,
        findings=tuple(adapter_result.findings) + tuple(orchestration_result.conditional_findings),
        compatibility_manifest=compatibility.manifest,
        route_warning=route_warning,
    )
