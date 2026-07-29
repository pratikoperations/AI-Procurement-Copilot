"""Isolated orchestration layer between the v1.3 workbook adapter and future integration."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
import re
from typing import Any, Mapping

from modules.rfq_conditional_rules import RuleFinding, evaluate_conditional_rules, evaluate_history_staleness, resolve_evaluation_date
from modules.rfq_evidence_coverage import EvidenceCoverage, aggregate_event, aggregate_item, quotation_coverage
from modules.rfq_normalization_bridge import NormalizationResult, normalize_record


@dataclass(frozen=True)
class HistoricalMatch:
    matched: bool
    method: str | None
    matched_history_row_id: str | None
    reason: str
    candidate_history_row_ids: tuple[str, ...] = ()
    automatic_match_level: str | None = None


@dataclass(frozen=True)
class EnrichedRecord:
    record: Any
    normalization: NormalizationResult
    eligible_for_analysis: bool
    evidence: EvidenceCoverage | None = None
    historical_match: HistoricalMatch | None = None


@dataclass(frozen=True)
class OrchestrationResult:
    adapter_result: Any
    evaluation_date: date
    evaluation_date_source: str
    comparison_currency: str | None
    enriched_quotes: tuple[EnrichedRecord, ...]
    enriched_history: tuple[EnrichedRecord, ...]
    conditional_findings: tuple[RuleFinding, ...]
    item_evidence: Mapping[str, EvidenceCoverage]
    event_coverage_percent: Decimal
    event_aggregation_method: str
    eligibility_status: str
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]


def _comparison_currency(adapter_result: Any, explicit: str | None):
    metadata = adapter_result.upload_metadata or {}
    value = str(metadata.get("BASE_CURRENCY") or explicit or "").strip().upper()
    return value or None


def _description_key(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value or "").casefold()).strip()


def _decimal(value: Any) -> Decimal | None:
    try:
        if value is None or str(value).strip() == "":
            return None
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None


def _history_match(quote: Any, eligible_history: tuple[EnrichedRecord, ...], *, approved_history_mappings: Mapping[str, str], manual_history_confirmations: set[tuple[str, str]]) -> HistoricalMatch:
    quote_values = quote.canonical_values
    quote_row_id = quote.provenance.source_row_id
    candidates = [item for item in eligible_history if item.eligible_for_analysis]
    ambiguous_ids: tuple[str, ...] = ()
    ambiguous_level: str | None = None

    material_id = quote_values.get("MATERIAL_ID")
    exact = [item for item in candidates if material_id and item.record.canonical_values.get("MATERIAL_ID") == material_id]
    if len(exact) == 1:
        row_id = exact[0].record.provenance.source_row_id
        return HistoricalMatch(True, "EXACT_MATERIAL_ID", row_id, "Unique exact material match.")
    if len(exact) > 1:
        ambiguous_ids = tuple(sorted(item.record.provenance.source_row_id for item in exact))
        ambiguous_level = "EXACT_MATERIAL_ID"

    if not exact:
        group = quote_values.get("MATERIAL_GROUP")
        description = _description_key(quote_values.get("MATERIAL_DESCRIPTION"))
        descriptive = [
            item for item in candidates
            if group and description
            and item.record.canonical_values.get("MATERIAL_GROUP") == group
            and _description_key(item.record.canonical_values.get("MATERIAL_DESCRIPTION")) == description
        ]
        if len(descriptive) == 1:
            row_id = descriptive[0].record.provenance.source_row_id
            return HistoricalMatch(True, "MATERIAL_GROUP_DESCRIPTION", row_id, "Unique material-group and normalized-description match.")
        if len(descriptive) > 1:
            ambiguous_ids = tuple(sorted(item.record.provenance.source_row_id for item in descriptive))
            ambiguous_level = "MATERIAL_GROUP_DESCRIPTION"

    mapped_row_id = approved_history_mappings.get(quote_row_id)
    mapped = [item for item in candidates if item.record.provenance.source_row_id == mapped_row_id]
    if len(mapped) == 1:
        return HistoricalMatch(True, "APPROVED_MAPPED_IDENTIFIER", mapped_row_id, "Approved deterministic history mapping.")

    manual = [item for item in candidates if (quote_row_id, item.record.provenance.source_row_id) in manual_history_confirmations]
    if len(manual) == 1:
        row_id = manual[0].record.provenance.source_row_id
        return HistoricalMatch(True, "MANUAL_CONFIRMATION", row_id, "Explicit manual history confirmation.")
    if len(manual) > 1:
        manual_ids = tuple(sorted(item.record.provenance.source_row_id for item in manual))
        return HistoricalMatch(False, None, None, "Multiple manual confirmations are ambiguous.", manual_ids, "MANUAL_CONFIRMATION")
    if ambiguous_ids:
        return HistoricalMatch(False, None, None, "Automatic history candidates are ambiguous and require approved mapping or manual confirmation.", ambiguous_ids, ambiguous_level)
    return HistoricalMatch(False, None, None, "No deterministic eligible history match.")


def orchestrate_adapter_result(adapter_result: Any, *, evaluation_date: date | None = None, comparison_currency: str | None = None, approved_free_text_row_ids: set[str] | None = None, approved_history_mappings: Mapping[str, str] | None = None, manual_history_confirmations: set[tuple[str, str]] | None = None, today: date | None = None) -> OrchestrationResult:
    approved_history_mappings = approved_history_mappings or {}
    manual_history_confirmations = manual_history_confirmations or set()
    resolved_date, date_source, date_findings = resolve_evaluation_date(adapter_result.upload_metadata, adapter_result.rfq_quotes, evaluation_date, today)
    currency = _comparison_currency(adapter_result, comparison_currency)
    quote_flags, history_flags, rule_findings = evaluate_conditional_rules(adapter_result, resolved_date, approved_free_text_row_ids=approved_free_text_row_ids)
    dynamic_findings: list[RuleFinding] = [*date_findings, *rule_findings]

    preliminary_history: list[EnrichedRecord] = []
    conditional_history_ids = {row_id for row_id, eligible in history_flags.items() if eligible}
    normalized_history_ids: set[str] = set()
    for record in adapter_result.po_history:
        norm = normalize_record(record.canonical_values, comparison_currency=currency, quantity_field="ORDER_QUANTITY", uom_field="ORDER_UOM", price_field="NET_PRICE")
        row_id = record.provenance.source_row_id
        eligible = row_id in conditional_history_ids and not norm.blockers
        if eligible:
            normalized_history_ids.add(row_id)
        elif row_id in conditional_history_ids and norm.blockers and adapter_result.mode == "FULL_SOURCING_REVIEW":
            dynamic_findings.append(RuleFinding("Warning", "HISTORY_NORMALIZATION_INVALID", f"Applicable history row {row_id} failed normalization and cannot support benchmark evidence.", row_id))
        preliminary_history.append(EnrichedRecord(record, norm, eligible))

    current_history_ids, stale_findings = evaluate_history_staleness(adapter_result.po_history, normalized_history_ids, resolved_date)
    dynamic_findings.extend(stale_findings)
    enriched_history = tuple(
        EnrichedRecord(item.record, item.normalization, item.eligible_for_analysis and item.record.provenance.source_row_id in current_history_ids)
        for item in preliminary_history
    )

    enriched_quotes: list[EnrichedRecord] = []
    item_coverages: dict[str, list[EvidenceCoverage]] = {}
    item_quantity_sets: dict[str, set[Decimal]] = {}
    for record in adapter_result.rfq_quotes:
        norm = normalize_record(record.canonical_values, comparison_currency=currency, quantity_field="QUOTED_QUANTITY", uom_field="QUOTATION_UOM", price_field="BASE_UNIT_PRICE")
        row_id = record.provenance.source_row_id
        eligible = quote_flags.get(row_id, False) and not norm.blockers
        match = _history_match(record, enriched_history, approved_history_mappings=approved_history_mappings, manual_history_confirmations=manual_history_confirmations)
        if not match.matched and match.candidate_history_row_ids:
            dynamic_findings.append(RuleFinding("Warning", "HISTORICAL_MATCH_AMBIGUOUS", f"Quotation {row_id} has ambiguous {match.automatic_match_level} history candidates {', '.join(match.candidate_history_row_ids)}; provide approved mapping or manual confirmation.", row_id))
        normalized_price = _decimal(norm.normalized_values.get("NORMALIZED_UNIT_PRICE"))
        if eligible and normalized_price == 0:
            dynamic_findings.append(RuleFinding("Warning", "ZERO_PRICE_REQUIRES_CLASSIFICATION", "Zero normalized unit price requires a separately governed classification before comparable-price evidence can be granted.", row_id))
        evidence = quotation_coverage(record.canonical_values, norm.normalized_values, has_history_match=match.matched) if eligible else None
        enriched_quotes.append(EnrichedRecord(record, norm, eligible, evidence, match))
        if evidence:
            key = f"{record.canonical_values.get('RFQ_NUMBER')}:{record.canonical_values.get('RFQ_ITEM')}"
            item_coverages.setdefault(key, []).append(evidence)
            quantity = _decimal(record.canonical_values.get("REQUESTED_QUANTITY"))
            if quantity is not None and quantity > 0:
                item_quantity_sets.setdefault(key, set()).add(quantity)

    item_quantities: dict[str, Decimal | None] = {}
    for key in item_coverages:
        quantities = item_quantity_sets.get(key, set())
        if len(quantities) > 1:
            dynamic_findings.append(RuleFinding("Blocking", "RFQ_ITEM_REQUESTED_QUANTITY_CONFLICT", f"RFQ item {key} has conflicting requested quantities."))
            item_quantities[key] = None
        elif len(quantities) == 1:
            item_quantities[key] = next(iter(quantities))
        else:
            item_quantities[key] = None

    item_results = {key: aggregate_item(values) for key, values in item_coverages.items()}
    event_score, aggregation = aggregate_event(item_results, item_quantities)
    findings = tuple(dynamic_findings)
    adapter_blockers = [finding.code for finding in adapter_result.findings if finding.severity in {"Fatal", "Blocking"}]
    orchestration_blockers = [finding.code for finding in findings if finding.severity in {"Fatal", "Blocking"}]
    quote_normalization_blockers = [blocker for item in enriched_quotes for blocker in item.normalization.blockers]
    blockers = tuple(dict.fromkeys((*adapter_blockers, *orchestration_blockers, *quote_normalization_blockers)))
    warnings = tuple(dict.fromkeys(finding.code for finding in findings if finding.severity == "Warning"))
    if blockers:
        status = "BLOCKED"
    elif event_score < Decimal("70"):
        status = "INSUFFICIENT_EVIDENCE"
    elif warnings or aggregation == "EQUAL_ITEM_WEIGHTED_FALLBACK":
        status = "ELIGIBLE_WITH_CONDITIONS"
    else:
        status = "ELIGIBLE_FOR_ANALYSIS"
    return OrchestrationResult(adapter_result, resolved_date, date_source, currency, tuple(enriched_quotes), enriched_history, findings, item_results, event_score, aggregation, status, blockers, warnings)
