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
from modules.ranking_input_semantics import EFFECTIVE_KEY_FIELDS, required_fields


def _record_id(record: CanonicalRankingRecord) -> str:
    return str(record.canonical_values.get("RANKING_INPUT_RECORD_ID") or record.provenance.source_row_id)


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


def _business_signature(record: CanonicalRankingRecord) -> tuple[Any, ...]:
    ignored = {
        "RANKING_INPUT_RECORD_ID", "RANKING_INPUT_VERSION", "SOURCE_ROW_ID",
        "SOURCE_FILE_NAME", "SOURCE_EXTRACTED_AT",
    }
    values = tuple(sorted((key, str(value)) for key, value in record.canonical_values.items() if key not in ignored))
    origins = tuple(sorted(record.value_origins.items()))
    return values, origins, record.source_evidence_status


def cross_row_findings(records: Sequence[CanonicalRankingRecord], finding_factory: Any) -> tuple[Any, ...]:
    findings: list[Any] = []
    by_id: dict[str, CanonicalRankingRecord] = {}
    by_effective_key: dict[tuple[Any, ...], list[CanonicalRankingRecord]] = defaultdict(list)
    by_scope: dict[tuple[Any, ...], list[CanonicalRankingRecord]] = defaultdict(list)
    for record in records:
        values = record.canonical_values
        record_id = _record_id(record)
        if record_id in by_id:
            prior = by_id[record_id]
            code = "EXACT_RANKING_INPUT_DUPLICATE" if _business_signature(prior) == _business_signature(record) else "CONTRADICTORY_RANKING_INPUT"
            severity = "Information" if code.startswith("EXACT") else "Fatal"
            findings.append(finding_factory(severity, code, f"Repeated ranking record '{record_id}'.", record.provenance.sheet, record.provenance.source_row_number, None))
        else:
            by_id[record_id] = record
        effective_key = tuple(values.get(name) for name in EFFECTIVE_KEY_FIELDS)
        by_effective_key[effective_key].append(record)
        scope_key = tuple(values.get(name) for name in (
            "SUPPLIER_ID", "PURCHASING_ORG", "RANKING_SCOPE", "MATERIAL_GROUP", "PLANT"
        ))
        by_scope[scope_key].append(record)

    for key, group in by_effective_key.items():
        signatures = {_business_signature(record) for record in group}
        if len(group) > 1:
            code = "EXACT_RANKING_INPUT_DUPLICATE" if len(signatures) == 1 else "CONTRADICTORY_RANKING_INPUT"
            severity = "Information" if code.startswith("EXACT") else "Fatal"
            findings.append(finding_factory(severity, code, f"Ranking records share effective key {key}.", group[-1].provenance.sheet, group[-1].provenance.source_row_number, None))
        versions = [int(record.canonical_values.get("RANKING_INPUT_VERSION") or 0) for record in group]
        if versions:
            highest = max(versions)
            winners = [record for record in group if int(record.canonical_values.get("RANKING_INPUT_VERSION") or 0) == highest]
            if len(winners) > 1 and len({_business_signature(record) for record in winners}) > 1:
                findings.append(finding_factory("Blocking", "RANKING_INPUT_VERSION_CONFLICT", f"Equal highest ranking versions conflict for key {key}.", winners[-1].provenance.sheet, winners[-1].provenance.source_row_number, None))
            if winners and not any(record.row_valid for record in winners) and any(record.row_valid for record in group if record not in winners):
                findings.append(finding_factory("Warning", "INVALID_HIGHER_RANKING_VERSION_IGNORED", f"Invalid higher ranking version ignored for key {key}.", winners[-1].provenance.sheet, winners[-1].provenance.source_row_number, None))

    for group in by_scope.values():
        ordered = sorted(group, key=lambda item: item.canonical_values.get("MEASUREMENT_PERIOD_START_DATE") or date.min)
        for prior, current in zip(ordered, ordered[1:]):
            prior_start = prior.canonical_values.get("MEASUREMENT_PERIOD_START_DATE")
            prior_end = prior.canonical_values.get("MEASUREMENT_PERIOD_END_DATE")
            current_start = current.canonical_values.get("MEASUREMENT_PERIOD_START_DATE")
            current_end = current.canonical_values.get("MEASUREMENT_PERIOD_END_DATE")
            same_period = prior_start == current_start and prior_end == current_end
            if not same_period and isinstance(prior_end, date) and isinstance(current_start, date) and current_start <= prior_end:
                findings.append(finding_factory("Blocking", "OVERLAPPING_RANKING_MEASUREMENT_PERIOD", "Ranking measurement periods overlap.", current.provenance.sheet, current.provenance.source_row_number, None))
    return tuple(findings)


def _select_version(records: Sequence[CanonicalRankingRecord]) -> tuple[CanonicalRankingRecord | None, bool]:
    if not records:
        return None, False
    latest_end = max((record.canonical_values.get("MEASUREMENT_PERIOD_END_DATE") or date.min) for record in records)
    period_records = [record for record in records if (record.canonical_values.get("MEASUREMENT_PERIOD_END_DATE") or date.min) == latest_end]
    highest = max(int(record.canonical_values.get("RANKING_INPUT_VERSION") or 0) for record in period_records)
    winners = [record for record in period_records if int(record.canonical_values.get("RANKING_INPUT_VERSION") or 0) == highest]
    valid_winners = [record for record in winners if record.row_valid]
    if len(valid_winners) > 1 and len({_business_signature(record) for record in valid_winners}) > 1:
        return None, True
    if valid_winners:
        return sorted(valid_winners, key=lambda item: item.provenance.source_row_number)[0], False
    valid_lower = [record for record in period_records if record.row_valid]
    if valid_lower:
        valid_lower.sort(key=lambda record: (-int(record.canonical_values.get("RANKING_INPUT_VERSION") or 0), record.provenance.source_row_number))
        return valid_lower[0], False
    return sorted(winners, key=lambda item: item.provenance.source_row_number)[0], False


def match_ranking_records(
    quotes: Sequence[Any],
    records: Sequence[CanonicalRankingRecord],
    evidence: Sequence[CanonicalFieldEvidenceResult],
    finding_factory: Any | None = None,
) -> tuple[RankingScopeMatch, ...]:
    matches: list[RankingScopeMatch] = []
    for quote_record in quotes:
        if not quote_record.active or not quote_record.eligible_for_analysis:
            continue
        quote = quote_record.canonical_values
        all_candidates = [record for record in records if record.active and _scope_matches(record.canonical_values, quote)]
        by_precedence: dict[int, list[CanonicalRankingRecord]] = defaultdict(list)
        for record in all_candidates:
            by_precedence[SCOPE_PRECEDENCE.get(str(record.canonical_values.get("RANKING_SCOPE")), 99)].append(record)
        chosen: CanonicalRankingRecord | None = None
        conflict = False
        fallback: CanonicalRankingRecord | None = None
        reason = "RANKING_SCOPE_UNMATCHED"
        blocking: list[Any] = []
        if by_precedence:
            specific_precedence = min(by_precedence)
            chosen, conflict = _select_version(by_precedence[specific_precedence])
            if conflict:
                reason = "RANKING_INPUT_VERSION_CONFLICT"
            elif chosen is not None and chosen.row_valid:
                reason = "MATCHED"
            else:
                for precedence in sorted(value for value in by_precedence if value > specific_precedence):
                    candidate, candidate_conflict = _select_version(by_precedence[precedence])
                    if candidate_conflict:
                        continue
                    if candidate is not None and candidate.row_valid:
                        fallback = candidate
                        break
                reason = "SPECIFIC_RANKING_SCOPE_INVALID_FALLBACK_USED" if fallback is not None else "RANKING_EVIDENCE_INVALID"
        if finding_factory and reason != "MATCHED":
            blocking.append(finding_factory("Blocking", reason, f"Ranking match resolved to {reason} for supplier '{quote.get('SUPPLIER_ID')}'.", "SUPPLIER_RANKING_INPUTS", None, None))
        record_id = None if chosen is None else _record_id(chosen)
        matches.append(RankingScopeMatch(
            rfq_number=str(quote.get("RFQ_NUMBER") or ""),
            rfq_item=str(quote.get("RFQ_ITEM") or ""),
            supplier_id=str(quote.get("SUPPLIER_ID") or ""),
            ranking_record_id=record_id,
            matched_scope=None if chosen is None else str(chosen.canonical_values.get("RANKING_SCOPE")),
            precedence=None if chosen is None else SCOPE_PRECEDENCE.get(str(chosen.canonical_values.get("RANKING_SCOPE"))),
            measurement_period_end=None if chosen is None else chosen.canonical_values.get("MEASUREMENT_PERIOD_END_DATE"),
            ranking_input_version=None if chosen is None else int(chosen.canonical_values.get("RANKING_INPUT_VERSION") or 0),
            eligible=reason == "MATCHED",
            reason=reason,
            fallback_record_id=None if fallback is None else _record_id(fallback),
            blocking_findings=tuple(blocking),
        ))
    return tuple(matches)


def calculate_mode_eligibility(
    mode: str,
    matches: Sequence[RankingScopeMatch],
    evidence: Sequence[CanonicalFieldEvidenceResult],
    finding_factory: Any | None = None,
    mapping_pending_suppliers: set[str] | None = None,
) -> tuple[RankingModeEligibility, ...]:
    by_record: dict[str, dict[str, CanonicalFieldEvidenceResult]] = defaultdict(dict)
    for item in evidence:
        by_record[item.ranking_record_id][item.canonical_field] = item
    required = required_fields(mode)
    mapping_pending_suppliers = mapping_pending_suppliers or set()
    results: list[RankingModeEligibility] = []
    for match in matches:
        items = by_record.get(match.ranking_record_id or "", {})
        statuses = {field: item.canonical_evidence_status for field, item in items.items()}
        valid = tuple(field for field in required if statuses.get(field) == "VALID")
        missing = tuple(field for field in required if statuses.get(field) == "MISSING" or field not in statuses)
        invalid = tuple(field for field in required if field in statuses and statuses[field] not in {"VALID", "MISSING"})
        blocking: list[Any] = list(match.blocking_findings)
        for field in (*missing, *invalid):
            item = items.get(field)
            if item:
                blocking.extend(finding for finding in item.validation_findings if getattr(finding, "severity", None) in {"Fatal", "Blocking"})
        if match.supplier_id in mapping_pending_suppliers:
            status = "RANKING_MAPPING_CONFIRMATION_REQUIRED"
        elif match.reason == "RANKING_INPUT_VERSION_CONFLICT" or any(status == "CONTRADICTORY" for status in statuses.values()):
            status = "RANKING_INPUTS_CONTRADICTORY"
        elif not match.ranking_record_id or match.reason == "RANKING_SCOPE_UNMATCHED":
            status = "RANKING_SCOPE_UNMATCHED"
        elif match.reason != "MATCHED":
            status = "RANKING_EVIDENCE_INVALID"
        elif invalid:
            status = "RANKING_EVIDENCE_INVALID"
        elif missing:
            status = "RANKING_INPUTS_MISSING"
        else:
            status = "RANKING_REVIEW_COMPLETE"
        if finding_factory and status != "RANKING_REVIEW_COMPLETE" and not blocking:
            blocking.append(finding_factory("Blocking", status, f"Ranking eligibility resolved to {status}.", "SUPPLIER_RANKING_INPUTS", None, None))
        results.append(RankingModeEligibility(
            mode, match.rfq_number, match.rfq_item, match.supplier_id, required,
            valid, missing, invalid, status, tuple(blocking),
        ))
    return tuple(results)
