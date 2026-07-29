"""Immutable contracts for governed analytical handoff."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Mapping

import pandas as pd

HANDOFF_CONTRACT_VERSION = "AIPC-E2-HANDOFF-1.3.1"
HANDOFF_DIGEST_VERSION = "AIPC-E2-HANDOFF-DIGEST-1.3.1"
HANDOFF_MANIFEST_VERSION = "AIPC-E2-HANDOFF-MANIFEST-1.3.1"
ENGINE_STAGES = (
    "INPUT_VALIDATION",
    "SCORING_TCO",
    "SCORED_OUTPUT_VALIDATION",
    "RECOMMENDATION",
    "ALLOCATION",
    "NEGOTIATION",
)

_STAGE_LABELS = {
    "INPUT_VALIDATION": "Input validation",
    "SCORING_TCO": "Supplier scoring and total cost",
    "SCORED_OUTPUT_VALIDATION": "Scored-output validation",
    "RECOMMENDATION": "Recommendation",
    "ALLOCATION": "Supplier allocation",
    "NEGOTIATION": "Negotiation preparation",
}
_STATUS_LABELS = {
    "PASSED": "Passed",
    "BLOCKED": "Stopped",
    "NOT_STARTED": "Not run",
}


@dataclass(frozen=True)
class HandoffFieldManifest:
    target_column: str
    target_dtype: str
    supplier_id: str
    source_domain: str
    source_field: str
    source_row_id: str
    source_record_id: str | None
    canonical_value: Any
    canonical_evidence_status: str | None
    value_origin: str
    transformation: str | None
    handoff_permitted: bool


@dataclass(frozen=True)
class HandoffSupplierManifest:
    supplier_id: str
    supplier_name: str
    quotation_source_row_id: str
    quotation_version: int
    ranking_record_id: str
    ranking_input_version: int
    ranking_scope: str
    ranking_measurement_end: date
    fields: tuple[HandoffFieldManifest, ...]


@dataclass(frozen=True)
class AnalyticalHandoffManifest:
    manifest_version: str
    contract_version: str
    upload_hash_sha256: str
    schema_version: str
    alias_registry_version: str
    upload_mode: str
    selected_sourcing_event_id: str
    selected_rfq_number: str
    selected_rfq_item: str
    evaluation_date: date
    analytical_currency: str
    comparison_uom: str
    suppliers: tuple[HandoffSupplierManifest, ...]
    assumptions_digest: str
    findings_digest: str
    dataframe_digest: str


@dataclass(frozen=True)
class AnalyticalHandoffResult:
    eligible: bool
    dataframe: pd.DataFrame | None
    manifest: AnalyticalHandoffManifest | None
    digest: str | None
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    findings: tuple[Any, ...]


class EngineStageResult:
    """Immutable stage evidence with a business-safe Streamlit representation."""

    __slots__ = (
        "_stage",
        "_status",
        "_input_digest",
        "_supplier_ids",
        "_finding_code",
        "_message",
    )

    def __init__(
        self,
        stage: str,
        status: str,
        input_digest: str,
        supplier_ids: tuple[str, ...],
        finding_code: str | None = None,
        message: str | None = None,
    ) -> None:
        object.__setattr__(self, "_stage", stage)
        object.__setattr__(self, "_status", status)
        object.__setattr__(self, "_input_digest", input_digest)
        object.__setattr__(self, "_supplier_ids", tuple(supplier_ids))
        object.__setattr__(self, "_finding_code", finding_code)
        object.__setattr__(self, "_message", message)

    def __setattr__(self, name: str, value: Any) -> None:
        raise AttributeError("EngineStageResult is immutable.")

    @property
    def stage(self) -> str:
        return self._stage

    @property
    def status(self) -> str:
        return self._status

    @property
    def input_digest(self) -> str:
        return self._input_digest

    @property
    def supplier_ids(self) -> tuple[str, ...]:
        return self._supplier_ids

    @property
    def finding_code(self) -> str | None:
        return self._finding_code

    @property
    def message(self) -> str | None:
        return self._message

    @property
    def __dict__(self) -> dict[str, str]:
        """Return only user-facing fields when Streamlit builds the audit table."""
        return {
            "Stage": _STAGE_LABELS.get(self._stage, self._stage.replace("_", " ").title()),
            "Status": _STATUS_LABELS.get(self._status, self._status.replace("_", " ").title()),
            "Suppliers": ", ".join(self._supplier_ids),
            "Details": self._message or "Completed without a blocking issue.",
        }


@dataclass(frozen=True)
class EngineExecutionResult:
    completed: bool
    outputs: Mapping[str, Any]
    stages: tuple[EngineStageResult, ...]
