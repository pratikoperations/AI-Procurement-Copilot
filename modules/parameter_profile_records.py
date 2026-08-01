"""Record contracts for future global/category/supplier/RFQ parameter resolution.

Gate 1A defines records only. Resolution and precedence are deliberately deferred.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any

SOURCE_LEVELS = ("global_default", "category_default", "supplier_specific", "rfq_scenario_override")
EVIDENCE_CLASSIFICATIONS = (
    "uploaded fact", "manually entered fact", "supplier-declared value",
    "historical measured value", "external benchmark", "system-derived value",
    "predicted value", "approved assumption", "default assumption",
    "existing undocumented controlled default",
)


@dataclass(frozen=True)
class ParameterProfileRecord:
    parameter_record_id: str
    assumption_id: str
    value: Any
    canonical_unit: str
    original_unit: str | None
    category: str | None
    supplier: str | None
    rfq_scenario: str | None
    source_level: str
    evidence_classification: str
    source_reference: str | None = None
    effective_date: str | None = None
    review_expiry_date: str | None = None
    confidence: float | None = None
    override_status: str = "not_overridden"
    override_reason: str | None = None
    approver: str | None = None
    version: str = "1.0"

    def __post_init__(self):
        if self.source_level not in SOURCE_LEVELS:
            raise ValueError(f"Unsupported source level: {self.source_level}")
        if self.evidence_classification not in EVIDENCE_CLASSIFICATIONS:
            raise ValueError(f"Unsupported evidence classification: {self.evidence_classification}")
        if self.confidence is not None and not 0 <= self.confidence <= 1:
            raise ValueError("Confidence must be between 0 and 1 or omitted.")
