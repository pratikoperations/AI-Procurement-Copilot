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
_SUPPORTED_SOURCE_LEVELS = tuple(PRECEDENCE)


class ParameterScopeValidationError(ValueError):
    """Raised when a source-level record violates its governed scope contract."""


class ParameterDateValidationError(ValueError):
    """Raised when a governed date field is not a valid ISO date."""


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


def _record_payload(
    record: ParameterProfileRecord, *, status: str, reason: str | None = None
) -> dict:
    payload = asdict(record)
    payload.update({"resolution_status": status, "resolution_reason": reason})
    return payload


def _payload_sort_key(payload: dict) -> tuple:
    return (
        payload.get("assumption_id") or "",
        -PRECEDENCE.get(payload.get("source_level"), 0),
        payload.get("parameter_record_id") or "",
        payload.get("version") or "",
        payload.get("resolution_reason") or "",
    )


def _validate_scope(record: ParameterProfileRecord) -> None:
    if record.source_level not in PRECEDENCE:
        supported = ", ".join(_SUPPORTED_SOURCE_LEVELS)
        raise ParameterScopeValidationError(
            f"Parameter record {record.parameter_record_id} has unsupported source level "
            f"{record.source_level!r}; supported source levels: {supported}"
        )

    fields = {
        "category": record.category,
        "supplier": record.supplier,
        "rfq_scenario": record.rfq_scenario,
    }
    if record.source_level == "global_default":
        violations = [name for name, value in fields.items() if value is not None]
    elif record.source_level == "category_default":
        violations = []
        if record.category is None:
            violations.append("category")
        if record.supplier is not None:
            violations.append("supplier")
        if record.rfq_scenario is not None:
            violations.append("rfq_scenario")
    elif record.source_level == "supplier_specific":
        violations = []
        if record.supplier is None:
            violations.append("supplier")
        if record.rfq_scenario is not None:
            violations.append("rfq_scenario")
    else:  # rfq_scenario_override
        violations = [] if record.rfq_scenario is not None else ["rfq_scenario"]

    if violations:
        fields_text = ", ".join(violations)
        raise ParameterScopeValidationError(
            f"Parameter record {record.parameter_record_id} at source level "
            f"{record.source_level} violates scope field(s): {fields_text}"
        )


def _parse_iso_date(record: ParameterProfileRecord, field_name: str) -> date | None:
    value = getattr(record, field_name)
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ParameterDateValidationError(
            f"Parameter record {record.parameter_record_id} has invalid "
            f"{field_name} value: {value}"
        ) from exc


def _applies(
    record: ParameterProfileRecord, *, category, supplier, rfq_scenario
) -> bool:
    if record.category is not None and record.category != category:
        return False
    if record.supplier is not None and record.supplier != supplier:
        return False
    if record.rfq_scenario is not None and record.rfq_scenario != rfq_scenario:
        return False
    return True


def _equivalent_signature(record: ParameterProfileRecord) -> tuple:
    return (record.value, record.canonical_unit, record.version)


def _record_sort_key(record: ParameterProfileRecord) -> tuple:
    return (-PRECEDENCE[record.source_level], record.parameter_record_id, record.version)


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
    unsorted_candidates = [
        record for record in candidates if record.assumption_id == assumption_id
    ]
    for record in unsorted_candidates:
        _validate_scope(record)
    candidate_list = sorted(unsorted_candidates, key=_record_sort_key)

    relevant = [
        record
        for record in candidate_list
        if _applies(
            record,
            category=category,
            supplier=supplier,
            rfq_scenario=rfq_scenario,
        )
    ]
    rejected: list[dict] = []
    valid: list[ParameterProfileRecord] = []
    for record in relevant:
        if expected_unit is not None and record.canonical_unit != expected_unit:
            rejected.append(
                _record_payload(record, status="rejected", reason="unit_mismatch")
            )
            continue
        effective_date = _parse_iso_date(record, "effective_date")
        expiry_date = _parse_iso_date(record, "review_expiry_date")
        if effective_date and effective_date > as_of:
            rejected.append(
                _record_payload(
                    record, status="rejected", reason="not_yet_effective"
                )
            )
            continue
        if expiry_date and expiry_date < as_of:
            rejected.append(
                _record_payload(record, status="rejected", reason="expired")
            )
            continue
        valid.append(record)

    valid = sorted(valid, key=_record_sort_key)
    available = tuple(
        _record_payload(record, status="candidate") for record in valid
    )
    if not valid:
        reason = "all_candidates_rejected" if relevant and rejected else "no_applicable_candidate"
        return ParameterResolutionResult(
            assumption_id,
            None,
            expected_unit,
            None,
            None,
            None,
            available,
            tuple(sorted(rejected, key=_payload_sort_key)),
            category,
            supplier,
            rfq_scenario,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            reason,
            False,
        )

    top_priority = max(PRECEDENCE[record.source_level] for record in valid)
    top = [record for record in valid if PRECEDENCE[record.source_level] == top_priority]
    first_signature = _equivalent_signature(top[0])
    if any(_equivalent_signature(record) != first_signature for record in top[1:]):
        raise ValueError(f"Conflicting same-priority records for {assumption_id}")

    selected = top[0]
    equivalent_duplicates = top[1:]
    rejected.extend(
        _record_payload(
            record,
            status="rejected",
            reason="duplicate_same_priority_equivalent",
        )
        for record in equivalent_duplicates
    )
    rejected.extend(
        _record_payload(record, status="rejected", reason="lower_precedence")
        for record in valid
        if record not in top
    )

    warnings: list[str] = []
    if selected.evidence_classification == UNDOCUMENTED_DEFAULT:
        warnings.append("Resolved using an existing undocumented controlled default.")
    if equivalent_duplicates:
        duplicate_ids = ", ".join(
            record.parameter_record_id for record in equivalent_duplicates
        )
        warnings.append(
            "Equivalent same-priority duplicate records were present: " + duplicate_ids
        )

    return ParameterResolutionResult(
        assumption_id=assumption_id,
        selected_value=selected.value,
        canonical_unit=selected.canonical_unit,
        original_unit=selected.original_unit,
        selected_source_level=selected.source_level,
        selected_source_record_id=selected.parameter_record_id,
        available_candidates=available,
        rejected_candidates=tuple(sorted(rejected, key=_payload_sort_key)),
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
        governance_warning=" ".join(warnings) or None,
        resolved=True,
    )
