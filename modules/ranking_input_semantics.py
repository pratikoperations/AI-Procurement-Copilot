"""Semantic validation and per-field evidence derivation for ranking inputs."""
from __future__ import annotations

from collections import defaultdict
from datetime import date
from decimal import Decimal
from typing import Any, Iterable, Mapping, Sequence

from modules.ranking_input_models import (
    CanonicalFieldEvidenceResult,
    CanonicalRankingRecord,
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
PERFORMANCE_FIELDS = {
    "OTIF_PERCENT", "QUALITY_PPM", "COMPLAINT_RATE_PERCENT", "CAPACITY_BUFFER_PERCENT"
}
FRESHNESS_MONTHS = {
    "OTIF_PERCENT": 12, "QUALITY_PPM": 12, "SUPPLIER_AUDIT_SCORE": 24,
    "COMPLAINT_RATE_PERCENT": 12, "CAPACITY_BUFFER_PERCENT": 12,
    "RECYCLABILITY_PERCENT": 24, "CERTIFICATION_SCORE": 0,
    "CARBON_SCORE": 24, "EPR_READINESS_SCORE": 12, "PCR_CONTENT_PERCENT": 24,
}
EFFECTIVE_KEY_FIELDS = (
    "SUPPLIER_ID", "PURCHASING_ORG", "RANKING_SCOPE", "MATERIAL_GROUP", "PLANT",
    "MEASUREMENT_PERIOD_START_DATE", "MEASUREMENT_PERIOD_END_DATE",
)


def required_fields(mode: str) -> tuple[str, ...]:
    return FULL_REVIEW_FIELDS if mode == "FULL_SOURCING_REVIEW" else QUICK_RFQ_FIELDS


def _months_old(end: date, evaluation: date) -> int:
    return (evaluation.year - end.year) * 12 + evaluation.month - end.month - (1 if evaluation.day < end.day else 0)


def choose_status(statuses: Iterable[str]) -> str:
    found = set(statuses)
    return next((status for status in STATUS_PRECEDENCE if status in found), "VALID")


def analyze_scale_ambiguity(records: Sequence[CanonicalRankingRecord]) -> set[str]:
    """Return fields whose observed values do not prove the governed 0-100 scale."""
    ambiguous: set[str] = set()
    for field in PERCENT_FIELDS | SCORE_FIELDS:
        values: list[Decimal] = []
        for record in records:
            value = record.canonical_values.get(field)
            if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
                continue
            values.append(Decimal(str(value)))
        if not values:
            continue
        fractional = any(Decimal("0") < value <= Decimal("1") for value in values)
        percentage_points = any(value > Decimal("1") for value in values)
        if fractional or (fractional and percentage_points):
            ambiguous.add(field)
    return ambiguous


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


def _origin_findings(
    field: str,
    origin: str | None,
    values: Mapping[str, Any],
    confirmed_origins: set[tuple[str, str]],
) -> tuple[list[str], bool]:
    codes: list[str] = []
    fatal = False
    if origin == "DEFAULTED_BY_ENGINE":
        return ["ENGINE_DEFAULT_ORIGIN_PROHIBITED"], True
    if origin not in VALUE_ORIGINS:
        return ["RANKING_VALUE_ORIGIN_MISSING" if origin is None else "RANKING_VALUE_ORIGIN_INVALID"], False
    if origin == "SOURCE_MAPPED":
        if not values.get("SOURCE_FILE_NAME") or not values.get("SOURCE_ROW_ID"):
            codes.append("RANKING_ORIGIN_EVIDENCE_MISSING")
    elif origin == "USER_CONFIRMED":
        if (field, origin) not in confirmed_origins:
            codes.append("RANKING_MAPPING_CONFIRMATION_REQUIRED")
    elif origin == "DERIVED_FROM_HISTORY":
        method_fields = {
            "OTIF_PERCENT": "OTIF_DERIVATION_METHOD",
            "QUALITY_PPM": "QUALITY_PPM_DERIVATION_METHOD",
        }
        method = method_fields.get(field)
        if method is None or not values.get(method) or not values.get("SOURCE_TRANSACTION_OR_REPORT"):
            codes.append("RANKING_ORIGIN_EVIDENCE_MISSING")
    elif origin == "REFERENCE_ENRICHED":
        if not values.get("SOURCE_SYSTEM") or not values.get("SOURCE_TRANSACTION_OR_REPORT"):
            codes.append("RANKING_ORIGIN_EVIDENCE_MISSING")
    return codes, fatal


def _contradiction_map(records: Sequence[CanonicalRankingRecord]) -> dict[tuple[str, str], tuple[Mapping[str, Any], ...]]:
    grouped: dict[tuple[Any, ...], list[CanonicalRankingRecord]] = defaultdict(list)
    for record in records:
        grouped[tuple(record.canonical_values.get(name) for name in EFFECTIVE_KEY_FIELDS)].append(record)
    result: dict[tuple[str, str], tuple[Mapping[str, Any], ...]] = {}
    for group in grouped.values():
        if len(group) < 2:
            continue
        for field in RANKING_FIELDS:
            populated = [record for record in group if record.canonical_values.get(field) is not None]
            signatures = {
                (str(record.canonical_values.get(field)), record.value_origins.get(field)) for record in populated
            }
            if len(signatures) <= 1:
                continue
            refs = tuple({
                "record_id": str(record.canonical_values.get("RANKING_INPUT_RECORD_ID") or record.provenance.source_row_id),
                "source_row_number": record.provenance.source_row_number,
                "value": record.canonical_values.get(field),
                "origin": record.value_origins.get(field),
            } for record in populated)
            for record in populated:
                record_id = str(record.canonical_values.get("RANKING_INPUT_RECORD_ID") or record.provenance.source_row_id)
                result[(record_id, field)] = refs
    return result


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
    confirmed_origins: set[tuple[str, str]] | None = None,
    schema_invalid: bool = False,
) -> tuple[str, tuple[str, ...]]:
    statuses: list[str] = []
    findings: list[str] = []
    confirmed_origins = confirmed_origins or set()
    if contradictory:
        statuses.append("CONTRADICTORY"); findings.append("CONTRADICTORY_RANKING_INPUT")
    if schema_invalid:
        statuses.append("UNVERIFIED"); findings.append("RANKING_ROW_SCHEMA_INVALID")
    if value is None:
        statuses.append("MISSING")
    elif isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
        statuses.append("INVALID_TYPE"); findings.append("RANKING_INPUT_INVALID_TYPE")
    else:
        number = Decimal(str(value))
        if field == "QUALITY_PPM" and number < 0:
            statuses.append("OUT_OF_RANGE"); findings.append("RANKING_INPUT_OUT_OF_RANGE")
        if field in PERCENT_FIELDS | SCORE_FIELDS and not Decimal("0") <= number <= Decimal("100"):
            statuses.append("OUT_OF_RANGE"); findings.append("RANKING_INPUT_OUT_OF_RANGE")
    if ambiguous_scope:
        statuses.append("AMBIGUOUS_SCOPE"); findings.append("RANKING_SCOPE_AMBIGUOUS")
    if ambiguous_scale and value is not None:
        statuses.append("AMBIGUOUS_SCALE"); findings.append("RANKING_INPUT_SCALE_AMBIGUOUS")
    if value is not None:
        origin_codes, origin_fatal = _origin_findings(field, origin, values, confirmed_origins)
        if origin_codes:
            statuses.append("UNVERIFIED"); findings.extend(origin_codes)
        if origin_fatal:
            statuses.append("CONTRADICTORY")
        if not _supporting_evidence(field, values):
            statuses.append("UNVERIFIED"); findings.append("RANKING_SUPPORTING_EVIDENCE_MISSING")
        start = values.get("MEASUREMENT_PERIOD_START_DATE")
        end = values.get("MEASUREMENT_PERIOD_END_DATE")
        if not isinstance(start, date) or not isinstance(end, date) or start > end or end > evaluation_date:
            statuses.append("UNVERIFIED"); findings.append("MEASUREMENT_PERIOD_INVALID")
        elif field == "CERTIFICATION_SCORE":
            valid_to = values.get("CERTIFICATION_VALID_TO")
            if not isinstance(valid_to, date) or valid_to < evaluation_date:
                statuses.append("STALE"); findings.append("CERTIFICATION_EXPIRED")
        elif _months_old(end, evaluation_date) > FRESHNESS_MONTHS[field]:
            statuses.append("STALE")
            findings.append("PERFORMANCE_INPUT_STALE" if field in PERFORMANCE_FIELDS else "AUDIT_EVIDENCE_STALE" if field == "SUPPLIER_AUDIT_SCORE" else "ESG_INPUT_STALE")
        if field in PERFORMANCE_FIELDS:
            count = values.get("PERFORMANCE_RECORD_COUNT")
            if not isinstance(count, int) or isinstance(count, bool) or count < 1:
                statuses.append("UNVERIFIED"); findings.append("PERFORMANCE_RECORD_COUNT_INVALID")
        if values.get("DATA_APPROVAL_STATUS") == "UNVERIFIED":
            statuses.append("UNVERIFIED"); findings.append("RANKING_SOURCE_UNVERIFIED")
    return choose_status(statuses or ["VALID"]), tuple(dict.fromkeys(findings))


def generate_evidence_results(
    records: Sequence[CanonicalRankingRecord],
    evaluation_date: date,
    finding_factory: Any,
    *,
    confirmed_origins: set[tuple[str, str]] | None = None,
    schema_invalid_rows: set[int] | None = None,
) -> tuple[CanonicalFieldEvidenceResult, ...]:
    results: list[CanonicalFieldEvidenceResult] = []
    ambiguous_fields = analyze_scale_ambiguity(records)
    contradictions = _contradiction_map(records)
    confirmed_origins = confirmed_origins or set()
    schema_invalid_rows = schema_invalid_rows or set()
    for record in records:
        values = record.canonical_values
        record_id = str(values.get("RANKING_INPUT_RECORD_ID") or record.provenance.source_row_id)
        supplier_id = str(values.get("SUPPLIER_ID") or "")
        for field in RANKING_FIELDS:
            origin = record.value_origins.get(field)
            competing = contradictions.get((record_id, field), ())
            status, codes = field_status(
                field, values.get(field), values, origin, evaluation_date,
                contradictory=bool(competing), ambiguous_scale=field in ambiguous_fields,
                confirmed_origins=confirmed_origins,
                schema_invalid=record.provenance.source_row_number in schema_invalid_rows,
            )
            source_reference = {
                "source_sheet": record.provenance.sheet,
                "source_row_number": record.provenance.source_row_number,
                "source_row_id": record.provenance.source_row_id,
                "source_filename": record.provenance.source_filename,
                "source_file_hash_sha256": record.provenance.source_file_hash_sha256,
                "upload_file_hash_sha256": record.provenance.upload_file_hash_sha256,
                "schema_version": record.provenance.schema_version,
                "alias_registry_version": record.provenance.alias_registry_version,
                "competing_sources": competing,
            }
            findings = tuple(
                finding_factory(
                    "Fatal" if code in {"CONTRADICTORY_RANKING_INPUT", "MEASUREMENT_PERIOD_INVALID", "ENGINE_DEFAULT_ORIGIN_PROHIBITED"} else "Blocking",
                    code, f"Ranking field '{field}' resolved to {status}.",
                    record.provenance.sheet, record.provenance.source_row_number, field,
                ) for code in codes
            )
            if record.source_evidence_status and record.source_evidence_status != status:
                findings += (finding_factory(
                    "Warning", "SOURCE_CANONICAL_STATUS_DISAGREEMENT",
                    f"Source claims {record.source_evidence_status}; canonical status is {status}.",
                    record.provenance.sheet, record.provenance.source_row_number, field,
                ),)
            results.append(CanonicalFieldEvidenceResult(
                record_id, supplier_id, field, values.get(field), status, origin,
                source_reference, findings,
            ))
    return tuple(results)
