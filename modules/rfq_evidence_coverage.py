"""Versioned evidence coverage for v1.3 sourcing analysis."""
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Mapping, Sequence

POLICY_VERSION="AIPC-EVIDENCE-COVERAGE-1.3.0"
WEIGHTS={"comparable_price":Decimal("25"),"quantity_availability":Decimal("15"),"commercial_terms":Decimal("10"),"delivery":Decimal("10"),"quality":Decimal("10"),"risk":Decimal("10"),"esg":Decimal("5"),"historical_benchmark":Decimal("15")}

@dataclass(frozen=True)
class EvidenceCoverage:
    policy_version: str
    dimension_results: Mapping[str,bool]
    coverage_percent: Decimal
    aggregation_method: str

def quotation_coverage(values: Mapping[str,Any], normalized: Mapping[str,Any], *, has_history_match: bool) -> EvidenceCoverage:
    quoted,requested=values.get("QUOTED_QUANTITY"),values.get("REQUESTED_QUANTITY")
    dims={
        "comparable_price": normalized.get("NORMALIZED_UNIT_PRICE") is not None,
        "quantity_availability": quoted is not None and requested is not None and (bool(values.get("FULL_QUANTITY_AVAILABLE")) or quoted>=requested),
        "commercial_terms": any(values.get(k) not in (None,"") for k in ("INCOTERMS_CODE","PAYMENT_TERMS_CODE","FREIGHT_AMOUNT","PACKING_AMOUNT","DISCOUNT_AMOUNT")),
        "delivery": any(values.get(k) not in (None,"") for k in ("LEAD_TIME_DAYS","PROMISED_DELIVERY_DATE")),
        "quality": any(values.get(k) not in (None,"") for k in ("TECHNICALLY_APPROVED","QUALITY_SCORE")),
        "risk": values.get("RISK_SCORE") is not None,
        "esg": values.get("ESG_SCORE") is not None,
        "historical_benchmark": has_history_match,
    }
    return EvidenceCoverage(POLICY_VERSION,dims,sum(weight for name,weight in WEIGHTS.items() if dims[name]),"PER_QUOTATION")

def aggregate_item(coverages: Sequence[EvidenceCoverage]) -> EvidenceCoverage:
    if not coverages: return EvidenceCoverage(POLICY_VERSION,{k:False for k in WEIGHTS},Decimal("0"),"NO_VALID_QUOTATIONS")
    minimum=min(coverages,key=lambda item:item.coverage_percent)
    return EvidenceCoverage(POLICY_VERSION,minimum.dimension_results,minimum.coverage_percent,"MINIMUM_VALID_SUPPLIER_COVERAGE")

def aggregate_event(item_results: Mapping[str,EvidenceCoverage], item_quantities: Mapping[str,Any]) -> tuple[Decimal,str]:
    if not item_results: return Decimal("0"),"NO_ITEMS"
    usable={k:Decimal(str(item_quantities[k])) for k in item_results if item_quantities.get(k) not in (None,0,"")}
    if len(usable)==len(item_results) and sum(usable.values())>0:
        total=sum(usable.values()); return sum(item_results[k].coverage_percent*usable[k] for k in item_results)/total,"REQUESTED_QUANTITY_WEIGHTED"
    return sum(v.coverage_percent for v in item_results.values())/Decimal(len(item_results)),"EQUAL_ITEM_WEIGHTED_FALLBACK"
