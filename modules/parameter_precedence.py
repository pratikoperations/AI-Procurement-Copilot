"""Deterministic parameter precedence for explainability traces only."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import date
from typing import Iterable

from modules.calculation_catalogue import UNDOCUMENTED_DEFAULT
from modules.parameter_profile_records import ParameterProfileRecord

PRECEDENCE = {
    "global_default": 1,
    "category_default": 2,
    "supplier_specific": 3,
    "rfq_scenario_override": 4,
}


@dataclass(frozen=True)
class ParameterResolutionResult:
    assumption_id: str
    selected_value: object | None
    canonical_unit: str | None
    original_unit: str | None
    selected_source_level: str | None
    selected_source_record_id: str | None
    available_candidates: tuple[dict, ...]
    rejected_candidates: tuple[dict, ...]
    category: str | None
    supplier: str | None
    rfq_scenario: str | None
    evidence_classification: str | None
    source_reference: str | None
    confidence: float | None
    version: str | None
    effective_date: str | None
    review_expiry_date: str | None
    override_status: str | None
    override_reason: str | None
    approver: str | None
    governance_warning: str | None
    resolved: bool


def _record_payload(record: ParameterProfileRecord, *, status: str, reason: str | None = None) -> dict:
    payload = asdict(record)
    payload.update({"resolution_status": status, "resolution_reason": reason})
    return payload


def _applies(record: ParameterProfileRecord, *, category, supplier, rfq_scenario) -> bool:
    if record.category is not None and record.category != category:
        return False
    if record.supplier is not None and record.supplier != supplier:
        return False
    if record.rfq_scenario is not None and record.rfq_scenario != rfq_scenario:
        return False
    return True


def resolve_parameter(
    assumption_id: str,
    candidates: Iterable[ParameterProfileRecord],
    *,
    category: str | None = None,
    supplier: str | None = None,
    rfq_scenario: str | None = None,
    expected_unit: str | None = None,
    as_of: date | None = None,
) -> ParameterResolutionResult:
    """Resolve one parameter using RFQ > supplier > category > global precedence."""
    as_of = as_of or date.today()
    relevant = [r for r in candidates if r.assumption_id == assumption_id and _applies(r, category=category, supplier=supplier, rfq_scenario=rfq_scenario)]
    rejected: list[dict] = []
    valid: list[ParameterProfileRecord] = []
    for record in relevant:
        if expected_unit is not None and record.canonical_unit != expected_unit:
            rejected.append(_record_payload(record, status="rejected", reason="unit_mismatch"))
            continue
        if record.review_expiry_date and date.fromisoformat(record.review_expiry_date) < as_of:
            rejected.append(_record_payload(record, status="rejected", reason="expired"))
            continue
        valid.append(record)
    available = tuple(_record_payload(r, status="candidate") for r in sorted(valid, key=lambda x: (PRECEDENCE[x.source_level], x.parameter_record_id), reverse=True))
    if not valid:
        reason = "no_applicable_candidate"
        if relevant and rejected:
            reason = "all_candidates_rejected"
        return ParameterResolutionResult(
            assumption_id, None, expected_unit, None, None, None, available, tuple(rejected),
            category, supplier, rfq_scenario, None, None, None, None, None, None,
            None, None, None, reason, False,
        )
    top_priority = max(PRECEDENCE[r.source_level] for r in valid)
    top = [r for r in valid if PRECEDENCE[r.source_level] == top_priority]
    signatures = {(repr(r.value), r.canonical_unit, r.version) for r in top}
    if len(signatures) > 1:
        raise ValueError(f"Conflicting same-priority records for {assumption_id}")
    selected = sorted(top, key=lambda r: r.parameter_record_id)[0]
    rejected.extend(
        _record_payload(r, status="rejected", reason="lower_precedence")
        for r in valid if r is not selected
    )
    warning = None
    if selected.evidence_classification == UNDOCUMENTED_DEFAULT:
        warning = "Resolved using an existing undocumented controlled default."
    return ParameterResolutionResult(
        assumption_id=assumption_id,
        selected_value=selected.value,
        canonical_unit=selected.canonical_unit,
        original_unit=selected.original_unit,
        selected_source_level=selected.source_level,
        selected_source_record_id=selected.parameter_record_id,
        available_candidates=available,
        rejected_candidates=tuple(rejected),
        category=category,
        supplier=supplier,
        rfq_scenario=rfq_scenario,
        evidence_classification=selected.evidence_classification,
        source_reference=selected.source_reference,
        confidence=selected.confidence,
        version=selected.version,
        effective_date=selected.effective_date,
        review_expiry_date=selected.review_expiry_date,
        override_status=selected.override_status,
        override_reason=selected.override_reason,
        approver=selected.approver,
        governance_warning=warning,
        resolved=True,
    )
