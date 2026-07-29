"""Semantic validation and per-field evidence derivation for ranking inputs."""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any, Iterable, Mapping, Sequence

from modules.ranking_input_models import (
    CanonicalFieldEvidenceResult,
    CanonicalRankingRecord,
    EVIDENCE_STATUSES,
    FULL_REVIEW_FIELDS,
    QUICK_RFQ_FIELDS,
    RANKING_FIELDS,
    STATUS_PRECEDENCE,
    VALUE_ORIGINS,
)


PERCENT_FIELDS = {
    "OTIF_PERCENT", "COMPLAINT_RATE_PERCENT", "CAPACITY_BUFFER_PERCENT",
    "RECYCLABILITY_PERCENT", "PCR_CONTENT_PERCENT",
}
SCORE_FIELDS = {
    "SUPPLIER_AUDIT_SCORE", "CERTIFICATION_SCORE", "CARBON_SCORE", "EPR_READINESS_SCORE"
}
FRESHNESS_MONTHS = {
    "OTIF_PERCENT": 12,
    "QUALITY_PPM": 12,
    "SUPPLIER_AUDIT_SCORE": 24,
    "COMPLAINT_RATE_PERCENT": 12,
    "CAPACITY_BUFFER_PERCENT": 12,
    "RECYCLABILITY_PERCENT": 24,
    "CERTIFICATION_SCORE": 0,
    "CARBON_SCORE": 24,
    "EPR_READINESS_SCORE": 12,
    "PCR_CONTENT_PERCENT": 24,
}


def required_fields(mode: str) -> tuple[str, ...]:
    return FULL_REVIEW_FIELDS if mode == "FULL_SOURCING_REVIEW" else QUICK_RFQ_FIELDS


def _months_old(end: date, evaluation: date) -> int:
    return (evaluation.year - end.year) * 12 + evaluation.month - end.month - (1 if evaluation.day < end.day else 0)


def choose_status(statuses: Iterable[str]) -> str:
    found = set(statuses)
    return next((status for status in STATUS_PRECEDENCE if status in found), "VALID")


def _supporting_evidence(field: str, values: Mapping[str, Any]) -> bool:
    required: dict[str, tuple[str, ...]] = {
        "SUPPLIER_AUDIT_SCORE": ("AUDIT_DATE", "AUDIT_STANDARD", "AUDIT_REFERENCE_ID"),
        "CERTIFICATION_SCORE": (
            "CERTIFICATION_TYPE", "CERTIFICATION_REFERENCE_ID", "CERTIFICATION_ISSUER",
            "CERTIFICATION_VALID_FROM", "CERTIFICATION_VALID_TO",
        ),
        "CARBON_SCORE": ("CARBON_SCORE_METHOD", "CARBON_SCORE_REFERENCE_ID"),
        "EPR_READINESS_SCORE": ("EPR_JURISDICTION", "EPR_EVIDENCE_REFERENCE_ID"),
        "PCR_CONTENT_PERCENT": ("PCR_VERIFICATION_METHOD", "PCR_EVIDENCE_REFERENCE_ID"),
    }
    return all(values.get(name) not in (None, "") for name in required.get(field, ()))


def field_status(
    field: str,
    value: Any,
    values: Mapping[str, Any],
    origin: str | None,
    evaluation_date: date,
    *,
    contradictory: bool = False,
    ambiguous_scope: bool = False,
    ambiguous_scale: bool = False,
) -> tuple[str, tuple[str, ...]]:
    statuses: list[str] = []
    findings: list[str] = []
    if contradictory:
        statuses.append("CONTRADICTORY")
        findings.append("CONTRADICTORY_RANKING_INPUT")
    if value is None:
        statuses.append("MISSING")
    elif isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
        statuses.append("INVALID_TYPE")
        findings.append("RANKING_INPUT_INVALID_TYPE")
    else:
        number = Decimal(str(value))
        if field == "QUALITY_PPM" and number < 0:
            statuses.append("OUT_OF_RANGE")
            findings.append("RANKING_INPUT_OUT_OF_RANGE")
        if field in PERCENT_FIELDS | SCORE_FIELDS and not Decimal("0") <= number <= Decimal("100"):
            statuses.append("OUT_OF_RANGE")
            findings.append("RANKING_INPUT_OUT_OF_RANGE")
    if ambiguous_scope:
        statuses.append("AMBIGUOUS_SCOPE")
        findings.append("RANKING_SCOPE_AMBIGUOUS")
    if ambiguous_scale:
        statuses.append("AMBIGUOUS_SCALE")
        findings.append("RANKING_INPUT_SCALE_AMBIGUOUS")
    if value is not None:
        if origin not in VALUE_ORIGINS:
            statuses.append("UNVERIFIED")
            findings.append("RANKING_VALUE_ORIGIN_MISSING" if origin is None else "RANKING_VALUE_ORIGIN_INVALID")
        if not _supporting_evidence(field, values):
            statuses.append("UNVERIFIED")
            findings.append("RANKING_SUPPORTING_EVIDENCE_MISSING")
        end = values.get("MEASUREMENT_PERIOD_END_DATE")
        if not isinstance(end, date) or end > evaluation_date:
            statuses.append("UNVERIFIED")
            findings.append("MEASUREMENT_PERIOD_INVALID")
        elif field == "CERTIFICATION_SCORE":
            valid_to = values.get("CERTIFICATION_VALID_TO")
            if not isinstance(valid_to, date) or valid_to < evaluation_date:
                statuses.append("STALE")
                findings.append("CERTIFICATION_EXPIRED")
        elif _months_old(end, evaluation_date) > FRESHNESS_MONTHS[field]:
            statuses.append("STALE")
            findings.append("PERFORMANCE_INPUT_STALE" if field in {
                "OTIF_PERCENT", "QUALITY_PPM", "COMPLAINT_RATE_PERCENT", "CAPACITY_BUFFER_PERCENT"
            } else "AUDIT_EVIDENCE_STALE" if field == "SUPPLIER_AUDIT_SCORE" else "ESG_INPUT_STALE")
        if values.get("DATA_APPROVAL_STATUS") == "UNVERIFIED":
            statuses.append("UNVERIFIED")
            findings.append("RANKING_SOURCE_UNVERIFIED")
    return choose_status(statuses or ["VALID"]), tuple(dict.fromkeys(findings))


def generate_evidence_results(
    records: Sequence[CanonicalRankingRecord],
    evaluation_date: date,
    finding_factory: Any,
) -> tuple[CanonicalFieldEvidenceResult, ...]:
    results: list[CanonicalFieldEvidenceResult] = []
    for record in records:
        values = record.canonical_values
        record_id = str(values.get("RANKING_INPUT_RECORD_ID") or record.provenance.source_row_id)
        supplier_id = str(values.get("SUPPLIER_ID") or "")
        for field in RANKING_FIELDS:
            origin = record.value_origins.get(field)
            status, codes = field_status(field, values.get(field), values, origin, evaluation_date)
            source_reference = {
                "source_sheet": record.provenance.sheet,
                "source_row_number": record.provenance.source_row_number,
                "source_row_id": record.provenance.source_row_id,
                "source_filename": record.provenance.source_filename,
                "source_file_hash_sha256": record.provenance.source_file_hash_sha256,
                "upload_file_hash_sha256": record.provenance.upload_file_hash_sha256,
                "schema_version": record.provenance.schema_version,
                "alias_registry_version": record.provenance.alias_registry_version,
            }
            findings = tuple(
                finding_factory(
                    "Fatal" if code in {"CONTRADICTORY_RANKING_INPUT", "MEASUREMENT_PERIOD_INVALID"} else "Blocking",
                    code,
                    f"Ranking field '{field}' resolved to {status}.",
                    record.provenance.sheet,
                    record.provenance.source_row_number,
                    field,
                )
                for code in codes
            )
            source_status = record.source_evidence_status
            if source_status and source_status != status:
                findings += (
                    finding_factory(
                        "Warning", "SOURCE_CANONICAL_STATUS_DISAGREEMENT",
                        f"Source claims {source_status}; canonical status is {status}.",
                        record.provenance.sheet, record.provenance.source_row_number, field,
                    ),
                )
            results.append(CanonicalFieldEvidenceResult(
                ranking_record_id=record_id,
                supplier_id=supplier_id,
                canonical_field=field,
                canonical_value=values.get(field),
                canonical_evidence_status=status,
                value_origin=origin,
                source_reference=source_reference,
                validation_findings=findings,
            ))
    return tuple(results)
