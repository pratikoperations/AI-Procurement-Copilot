"""Immutable contracts for governed analytical handoff."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

import pandas as pd

HANDOFF_CONTRACT_VERSION = "AIPC-E2-HANDOFF-1.3.1"
HANDOFF_DIGEST_VERSION = "AIPC-E2-HANDOFF-DIGEST-1.3.1"
HANDOFF_MANIFEST_VERSION = "AIPC-E2-HANDOFF-MANIFEST-1.3.1"


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
