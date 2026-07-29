"""Isolated orchestration layer between the v1.3 workbook adapter and future integration."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any, Mapping
from modules.rfq_conditional_rules import RuleFinding,evaluate_conditional_rules,resolve_evaluation_date
from modules.rfq_evidence_coverage import EvidenceCoverage,aggregate_event,aggregate_item,quotation_coverage
from modules.rfq_normalization_bridge import NormalizationResult,normalize_record

@dataclass(frozen=True)
class EnrichedRecord:
    record: Any
    normalization: NormalizationResult
    eligible_for_analysis: bool
    evidence: EvidenceCoverage|None=None

@dataclass(frozen=True)
class OrchestrationResult:
    adapter_result: Any
    evaluation_date: date
    evaluation_date_source: str
    comparison_currency: str|None
    enriched_quotes: tuple[EnrichedRecord,...]
    enriched_history: tuple[EnrichedRecord,...]
    conditional_findings: tuple[RuleFinding,...]
    item_evidence: Mapping[str,EvidenceCoverage]
    event_coverage_percent: Decimal
    event_aggregation_method: str
    eligibility_status: str
    blockers: tuple[str,...]
    warnings: tuple[str,...]

def _comparison_currency(adapter_result: Any, explicit: str|None):
    metadata=adapter_result.upload_metadata or {}; value=str(metadata.get("BASE_CURRENCY") or explicit or "").strip().upper(); return value or None

def orchestrate_adapter_result(adapter_result: Any, *, evaluation_date: date|None=None, comparison_currency: str|None=None, approved_free_text_row_ids: set[str]|None=None, tax_non_recoverable: bool=False, today: date|None=None) -> OrchestrationResult:
    resolved_date,date_source,date_findings=resolve_evaluation_date(adapter_result.upload_metadata,adapter_result.rfq_quotes,evaluation_date,today)
    currency=_comparison_currency(adapter_result,comparison_currency)
    quote_flags,history_flags,rule_findings=evaluate_conditional_rules(adapter_result,resolved_date,approved_free_text_row_ids=approved_free_text_row_ids)
    findings=tuple((*date_findings,*rule_findings)); history_by_material=set(); enriched_history=[]
    for record in adapter_result.po_history:
        norm=normalize_record(record.canonical_values,comparison_currency=currency,quantity_field="ORDER_QUANTITY",uom_field="ORDER_UOM",price_field="NET_PRICE")
        eligible=history_flags.get(record.provenance.source_row_id,False) and not norm.blockers
        if eligible and record.canonical_values.get("MATERIAL_ID"): history_by_material.add(record.canonical_values.get("MATERIAL_ID"))
        enriched_history.append(EnrichedRecord(record,norm,eligible))
    enriched_quotes=[]; item_coverages={}; item_quantities={}
    for record in adapter_result.rfq_quotes:
        norm=normalize_record(record.canonical_values,comparison_currency=currency,quantity_field="QUOTED_QUANTITY",uom_field="QUOTATION_UOM",price_field="BASE_UNIT_PRICE")
        eligible=quote_flags.get(record.provenance.source_row_id,False) and not norm.blockers
        material_id=record.canonical_values.get("MATERIAL_ID")
        evidence=quotation_coverage(record.canonical_values,norm.normalized_values,has_history_match=bool(material_id and material_id in history_by_material)) if eligible else None
        enriched_quotes.append(EnrichedRecord(record,norm,eligible,evidence))
        if evidence:
            key=f"{record.canonical_values.get('RFQ_NUMBER')}:{record.canonical_values.get('RFQ_ITEM')}"; item_coverages.setdefault(key,[]).append(evidence); item_quantities[key]=record.canonical_values.get("REQUESTED_QUANTITY")
    item_results={key:aggregate_item(values) for key,values in item_coverages.items()}; event_score,aggregation=aggregate_event(item_results,item_quantities)
    adapter_blockers=[f.code for f in adapter_result.findings if f.severity in {"Fatal","Blocking"}]
    orchestration_blockers=[f.code for f in findings if f.severity in {"Fatal","Blocking"}]
    normalization_blockers=[b for item in (*enriched_quotes,*enriched_history) for b in item.normalization.blockers]
    blockers=tuple(dict.fromkeys((*adapter_blockers,*orchestration_blockers,*normalization_blockers))); warnings=tuple(dict.fromkeys(f.code for f in findings if f.severity=="Warning"))
    if blockers: status="BLOCKED"
    elif event_score<Decimal("70"): status="INSUFFICIENT_EVIDENCE"
    elif warnings or aggregation=="EQUAL_ITEM_WEIGHTED_FALLBACK": status="ELIGIBLE_WITH_CONDITIONS"
    else: status="ELIGIBLE_FOR_ANALYSIS"
    return OrchestrationResult(adapter_result,resolved_date,date_source,currency,tuple(enriched_quotes),tuple(enriched_history),findings,item_results,event_score,aggregation,status,blockers,warnings)
