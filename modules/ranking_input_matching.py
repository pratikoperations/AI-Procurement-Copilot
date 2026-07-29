"""Cross-row controls, scope matching, and mode eligibility for ranking inputs."""
from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Any, Mapping, Sequence

from modules.ranking_input_models import (
    CanonicalFieldEvidenceResult,
    CanonicalRankingRecord,
    RankingModeEligibility,
    RankingScopeMatch,
    SCOPE_PRECEDENCE,
)
from modules.ranking_input_semantics import required_fields


def _scope_matches(values: Mapping[str, Any], quote: Mapping[str, Any]) -> bool:
    if str(values.get("SUPPLIER_ID")) != str(quote.get("SUPPLIER_ID")):
        return False
    if str(values.get("PURCHASING_ORG")) != str(quote.get("PURCHASING_ORG")):
        return False
    scope = values.get("RANKING_SCOPE")
    if scope in {"MATERIAL_GROUP", "PLANT_MATERIAL_GROUP"} and str(values.get("MATERIAL_GROUP")) != str(quote.get("MATERIAL_GROUP")):
        return False
    if scope == "PLANT_MATERIAL_GROUP" and str(values.get("PLANT")) != str(quote.get("PLANT")):
        return False
    return scope in SCOPE_PRECEDENCE


def cross_row_findings(records: Sequence[CanonicalRankingRecord], finding_factory: Any) -> tuple[Any, ...]:
    findings: list[Any] = []
    by_id: dict[str, CanonicalRankingRecord] = {}
    by_key: dict[tuple[Any, ...], list[CanonicalRankingRecord]] = defaultdict(list)
    for record in records:
        values = record.canonical_values
        record_id = str(values.get("RANKING_INPUT_RECORD_ID") or "")
        if record_id in by_id:
            prior = by_id[record_id]
            if prior.canonical_values == record.canonical_values and prior.value_origins == record.value_origins:
                findings.append(finding_factory("Information", "EXACT_RANKING_INPUT_DUPLICATE", f"Duplicate ranking record '{record_id}'.", record.provenance.sheet, record.provenance.source_row_number, None))
            else:
                findings.append(finding_factory("Fatal", "CONTRADICTORY_RANKING_INPUT", f"Conflicting ranking record '{record_id}'.", record.provenance.sheet, record.provenance.source_row_number, None))
        else:
            by_id[record_id] = record
        key = tuple(values.get(name) for name in (
            "SUPPLIER_ID", "PURCHASING_ORG", "RANKING_SCOPE", "MATERIAL_GROUP", "PLANT"
        ))
        by_key[key].append(record)
    for group in by_key.values():
        ordered = sorted(group, key=lambda item: item.canonical_values.get("MEASUREMENT_PERIOD_START_DATE") or date.min)
        for prior, current in zip(ordered, ordered[1:]):
            prior_end = prior.canonical_values.get("MEASUREMENT_PERIOD_END_DATE")
            current_start = current.canonical_values.get("MEASUREMENT_PERIOD_START_DATE")
            if isinstance(prior_end, date) and isinstance(current_start, date) and current_start <= prior_end:
                findings.append(finding_factory("Blocking", "OVERLAPPING_RANKING_MEASUREMENT_PERIOD", "Ranking measurement periods overlap.", current.provenance.sheet, current.provenance.source_row_number, None))
    return tuple(findings)


def match_ranking_records(
    quotes: Sequence[Any],
    records: Sequence[CanonicalRankingRecord],
    evidence: Sequence[CanonicalFieldEvidenceResult],
) -> tuple[RankingScopeMatch, ...]:
    invalid_ids = {
        item.ranking_record_id for item in evidence if item.canonical_evidence_status not in {"VALID", "MISSING"}
    }
    matches: list[RankingScopeMatch] = []
    for quote_record in quotes:
        if not quote_record.active or not quote_record.eligible_for_analysis:
            continue
        quote = quote_record.canonical_values
        candidates = [record for record in records if record.row_valid and record.active and _scope_matches(record.canonical_values, quote)]
        candidates.sort(key=lambda record: (
            SCOPE_PRECEDENCE.get(str(record.canonical_values.get("RANKING_SCOPE")), 99),
            -(record.canonical_values.get("MEASUREMENT_PERIOD_END_DATE") or date.min).toordinal(),
            -int(record.canonical_values.get("RANKING_INPUT_VERSION") or 0),
        ))
        chosen = candidates[0] if candidates else None
        record_id = None if chosen is None else str(chosen.canonical_values.get("RANKING_INPUT_RECORD_ID") or chosen.provenance.source_row_id)
        eligible = chosen is not None and record_id not in invalid_ids
        reason = "MATCHED" if eligible else "RANKING_SCOPE_UNMATCHED" if chosen is None else "RANKING_EVIDENCE_INVALID"
        matches.append(RankingScopeMatch(
            rfq_number=str(quote.get("RFQ_NUMBER") or ""),
            rfq_item=str(quote.get("RFQ_ITEM") or ""),
            supplier_id=str(quote.get("SUPPLIER_ID") or ""),
            ranking_record_id=record_id,
            matched_scope=None if chosen is None else str(chosen.canonical_values.get("RANKING_SCOPE")),
            precedence=None if chosen is None else SCOPE_PRECEDENCE.get(str(chosen.canonical_values.get("RANKING_SCOPE"))),
            measurement_period_end=None if chosen is None else chosen.canonical_values.get("MEASUREMENT_PERIOD_END_DATE"),
            ranking_input_version=None if chosen is None else int(chosen.canonical_values.get("RANKING_INPUT_VERSION") or 0),
            eligible=eligible,
            reason=reason,
        ))
    return tuple(matches)


def calculate_mode_eligibility(
    mode: str,
    matches: Sequence[RankingScopeMatch],
    evidence: Sequence[CanonicalFieldEvidenceResult],
) -> tuple[RankingModeEligibility, ...]:
    by_record: dict[str, dict[str, str]] = defaultdict(dict)
    for item in evidence:
        by_record[item.ranking_record_id][item.canonical_field] = item.canonical_evidence_status
    required = required_fields(mode)
    results: list[RankingModeEligibility] = []
    for match in matches:
        statuses = by_record.get(match.ranking_record_id or "", {})
        valid = tuple(field for field in required if statuses.get(field) == "VALID")
        missing = tuple(field for field in required if statuses.get(field) == "MISSING" or field not in statuses)
        invalid = tuple(field for field in required if field in statuses and statuses[field] not in {"VALID", "MISSING"})
        if not match.ranking_record_id:
            status = "RANKING_SCOPE_UNMATCHED"
        elif invalid:
            status = "RANKING_EVIDENCE_INVALID"
        elif missing:
            status = "RANKING_INPUTS_MISSING"
        else:
            status = "RANKING_REVIEW_COMPLETE"
        results.append(RankingModeEligibility(
            mode=mode,
            rfq_number=match.rfq_number,
            rfq_item=match.rfq_item,
            supplier_id=match.supplier_id,
            required_fields=required,
            valid_fields=valid,
            missing_fields=missing,
            invalid_fields=invalid,
            status=status,
            blocking_findings=(),
        ))
    return tuple(results)
