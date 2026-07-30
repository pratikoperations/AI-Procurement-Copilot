"""Governed Build Group E review state and policy contracts."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from hashlib import sha256
import json
from typing import Any, Iterable, Mapping

WARNING_POLICY_VERSION = "AIPC-COMPATIBILITY-WARNING-DISPOSITION-1.3.1"


class ReviewState(str, Enum):
    ROUTE_DISABLED = "ROUTE_DISABLED"
    NO_FILE = "NO_FILE"
    FILE_RECEIVED = "FILE_RECEIVED"
    ADAPTER_FATAL = "ADAPTER_FATAL"
    MAPPING_CONFIRMATION_REQUIRED = "MAPPING_CONFIRMATION_REQUIRED"
    EVENT_SELECTION_REQUIRED = "EVENT_SELECTION_REQUIRED"
    ADAPTER_READY = "ADAPTER_READY"
    ORCHESTRATION_BLOCKED = "ORCHESTRATION_BLOCKED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    CONDITIONAL_REVIEW_REQUIRED = "CONDITIONAL_REVIEW_REQUIRED"
    ANALYTICAL_REVIEW_READY = "ANALYTICAL_REVIEW_READY"
    ITEM_SELECTION_REQUIRED = "ITEM_SELECTION_REQUIRED"
    ANALYSIS_INCOMPATIBLE = "ANALYSIS_INCOMPATIBLE"
    REVIEW_ONLY_COMPLETE = "REVIEW_ONLY_COMPLETE"
    READY_FOR_HANDOFF = "READY_FOR_HANDOFF"
    HANDOFF_CONFIRMED = "HANDOFF_CONFIRMED"


class WarningDisposition(str, Enum):
    DISPLAY_ONLY = "DISPLAY_ONLY"
    ACKNOWLEDGEMENT_REQUIRED = "ACKNOWLEDGEMENT_REQUIRED"
    COMPATIBILITY_BLOCKING = "COMPATIBILITY_BLOCKING"


WARNING_DISPOSITIONS: Mapping[str, Mapping[str, WarningDisposition]] = {
    "SYSTEM_DATE_FALLBACK": {"QUICK_RFQ": WarningDisposition.COMPATIBILITY_BLOCKING, "FULL_SOURCING_REVIEW": WarningDisposition.COMPATIBILITY_BLOCKING},
    "FULL_REVIEW_HISTORY_EMPTY": {"QUICK_RFQ": WarningDisposition.DISPLAY_ONLY, "FULL_SOURCING_REVIEW": WarningDisposition.COMPATIBILITY_BLOCKING},
    "HISTORY_ROW_OUT_OF_WINDOW": {"QUICK_RFQ": WarningDisposition.DISPLAY_ONLY, "FULL_SOURCING_REVIEW": WarningDisposition.ACKNOWLEDGEMENT_REQUIRED},
    "HISTORY_STALE": {"QUICK_RFQ": WarningDisposition.ACKNOWLEDGEMENT_REQUIRED, "FULL_SOURCING_REVIEW": WarningDisposition.ACKNOWLEDGEMENT_REQUIRED},
    "HISTORY_NORMALIZATION_INVALID": {"QUICK_RFQ": WarningDisposition.DISPLAY_ONLY, "FULL_SOURCING_REVIEW": WarningDisposition.ACKNOWLEDGEMENT_REQUIRED},
    "HISTORICAL_MATCH_AMBIGUOUS": {"QUICK_RFQ": WarningDisposition.ACKNOWLEDGEMENT_REQUIRED, "FULL_SOURCING_REVIEW": WarningDisposition.COMPATIBILITY_BLOCKING},
    "ZERO_PRICE_REQUIRES_CLASSIFICATION": {"QUICK_RFQ": WarningDisposition.COMPATIBILITY_BLOCKING, "FULL_SOURCING_REVIEW": WarningDisposition.COMPATIBILITY_BLOCKING},
}


@dataclass(frozen=True)
class ReviewIdentity:
    upload_hash_sha256: str
    schema_version: str
    alias_registry_version: str
    selected_sourcing_event_id: str
    selected_rfq_number: str
    selected_rfq_item: str
    canonical_engine_currency: str
    display_currency_mode: str
    evaluation_date: date
    evaluation_date_source: str
    adapter_finding_digest: str
    orchestration_finding_digest: str
    compatibility_manifest_digest: str
    approved_mapping_digest: str
    approved_history_mapping_digest: str
    manual_history_confirmation_digest: str
    warning_acknowledgement_digest: str = ""
    analytical_assumptions_digest: str = ""
    dataframe_digest: str = ""
    handoff_contract_version: str = ""

    @property
    def digest(self) -> str:
        return sha256(json.dumps(self.__dict__, sort_keys=True, default=str).encode("utf-8")).hexdigest()


def stable_digest(value: Any) -> str:
    return sha256(json.dumps(value, sort_keys=True, default=str).encode("utf-8")).hexdigest()


def warning_disposition(code: str, mode: str) -> WarningDisposition:
    policy = WARNING_DISPOSITIONS.get(code)
    if policy is None:
        return WarningDisposition.COMPATIBILITY_BLOCKING
    return policy.get(mode, WarningDisposition.COMPATIBILITY_BLOCKING)


def classify_orchestration_state(status: str) -> ReviewState:
    return {
        "BLOCKED": ReviewState.ORCHESTRATION_BLOCKED,
        "INSUFFICIENT_EVIDENCE": ReviewState.INSUFFICIENT_EVIDENCE,
        "ELIGIBLE_WITH_CONDITIONS": ReviewState.CONDITIONAL_REVIEW_REQUIRED,
        "ELIGIBLE_FOR_ANALYSIS": ReviewState.ANALYTICAL_REVIEW_READY,
    }.get(status, ReviewState.ORCHESTRATION_BLOCKED)


def warning_controls(warning_codes: Iterable[str], mode: str, acknowledged_codes: Iterable[str] = ()) -> tuple[tuple[str, ...], tuple[str, ...]]:
    acknowledged = set(acknowledged_codes)
    blocking: list[str] = []
    outstanding: list[str] = []
    for code in dict.fromkeys(warning_codes):
        disposition = warning_disposition(code, mode)
        if disposition is WarningDisposition.COMPATIBILITY_BLOCKING:
            blocking.append(code)
        elif disposition is WarningDisposition.ACKNOWLEDGEMENT_REQUIRED and code not in acknowledged:
            outstanding.append(code)
    return tuple(blocking), tuple(outstanding)
