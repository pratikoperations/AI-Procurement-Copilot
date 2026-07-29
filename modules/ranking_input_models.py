"""Immutable models for governed supplier ranking-input review."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Mapping

RANKING_FIELDS = (
    "OTIF_PERCENT", "QUALITY_PPM", "SUPPLIER_AUDIT_SCORE",
    "COMPLAINT_RATE_PERCENT", "CAPACITY_BUFFER_PERCENT",
    "RECYCLABILITY_PERCENT", "CERTIFICATION_SCORE", "CARBON_SCORE",
    "EPR_READINESS_SCORE", "PCR_CONTENT_PERCENT",
)
QUICK_RFQ_FIELDS = (
    "OTIF_PERCENT", "QUALITY_PPM", "SUPPLIER_AUDIT_SCORE",
    "RECYCLABILITY_PERCENT", "CERTIFICATION_SCORE",
)
FULL_REVIEW_FIELDS = RANKING_FIELDS
VALUE_ORIGINS = {
    "SOURCE_MAPPED", "USER_CONFIRMED", "DERIVED_FROM_HISTORY", "REFERENCE_ENRICHED"
}
EVIDENCE_STATUSES = {
    "VALID", "MISSING", "INVALID_TYPE", "OUT_OF_RANGE", "STALE",
    "AMBIGUOUS_SCOPE", "AMBIGUOUS_SCALE", "CONTRADICTORY", "UNVERIFIED",
}
STATUS_PRECEDENCE = (
    "CONTRADICTORY", "INVALID_TYPE", "OUT_OF_RANGE", "AMBIGUOUS_SCOPE",
    "AMBIGUOUS_SCALE", "STALE", "UNVERIFIED", "MISSING", "VALID",
)
SCOPE_PRECEDENCE = {
    "PLANT_MATERIAL_GROUP": 1,
    "MATERIAL_GROUP": 2,
    "PURCHASING_ORG": 3,
    "SUPPLIER_GLOBAL": 4,
}


@dataclass(frozen=True)
class RankingMappingConfirmation:
    upload_hash_sha256: str
    schema_version: str
    alias_registry_version: str
    sheet: str
    source_header: str
    canonical_field: str
    detected_scale: str
    value_origin: str


@dataclass(frozen=True)
class CanonicalRankingRecord:
    canonical_values: Mapping[str, Any]
    value_origins: Mapping[str, str]
    source_evidence_status: str | None
    provenance: Any
    row_valid: bool = True
    active: bool = True


@dataclass(frozen=True)
class CanonicalFieldEvidenceResult:
    ranking_record_id: str
    supplier_id: str
    canonical_field: str
    canonical_value: Any
    canonical_evidence_status: str
    value_origin: str | None
    source_reference: Mapping[str, Any]
    validation_findings: tuple[Any, ...]


@dataclass(frozen=True)
class RankingScopeMatch:
    rfq_number: str
    rfq_item: str
    supplier_id: str
    ranking_record_id: str | None
    matched_scope: str | None
    precedence: int | None
    measurement_period_end: date | None
    ranking_input_version: int | None
    eligible: bool
    reason: str
    fallback_record_id: str | None = None
    blocking_findings: tuple[Any, ...] = ()


@dataclass(frozen=True)
class RankingModeEligibility:
    mode: str
    rfq_number: str
    rfq_item: str
    supplier_id: str
    required_fields: tuple[str, ...]
    valid_fields: tuple[str, ...]
    missing_fields: tuple[str, ...]
    invalid_fields: tuple[str, ...]
    status: str
    blocking_findings: tuple[Any, ...]
