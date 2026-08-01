"""Read-only SourceMate Basic evidence presentation.

This module presents existing catalogue, provenance, coverage and export-registry
metadata. It does not retrieve external evidence or claim external verification.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import date
from typing import Any, Iterable, Mapping

from modules.export_evidence_registry import EXPORT_EVIDENCE
from modules.reconciliation_coverage import adapter_coverage_classification

SOURCEMATE_CONTRACT_VERSION = "AIPC-SOURCEMATE-BASIC-1.0"
SOURCEMATE_LIMITATIONS = (
    "Registered references are internal evidence locations, not external verification.",
    "SourceMate Basic does not browse the web, ingest documents, run OCR, use RAG, or invent links.",
    "Unavailable evidence is disclosed and is never reconstructed.",
    "Human approval remains mandatory; no autonomous award or production allocation is performed.",
)


def _is_review_due(value: Any, today: date | None = None) -> bool:
    if not value:
        return False
    today = today or date.today()
    try:
        return date.fromisoformat(str(value)) < today
    except ValueError:
        return False


def build_sourcemate_summary(
    *,
    calculation: Mapping[str, Any],
    assumptions: Iterable[Mapping[str, Any]],
    coverage_id: str,
    runtime_evidence: Mapping[str, str] | None = None,
    today: date | None = None,
) -> dict[str, Any]:
    """Build a stable evidence summary without mutating source records."""
    calculation_copy = deepcopy(dict(calculation))
    assumption_copies = [deepcopy(dict(item)) for item in assumptions]
    runtime_evidence = dict(runtime_evidence or {})
    calculation_id = str(calculation_copy.get("calculation_id") or "")
    evidence_rows = []
    for evidence in EXPORT_EVIDENCE:
        if calculation_id not in evidence.calculation_ids:
            continue
        evidence_rows.append({
            "evidence_id": evidence.evidence_id,
            "export_type": evidence.export_type,
            "location": evidence.location,
            "audience": evidence.audience,
            "source_file": evidence.source_file,
            "source_function": evidence.source_function,
            "schema_change": evidence.schema_change,
            "registration_status": "registered",
            "runtime_presence": runtime_evidence.get(evidence.evidence_id, "not independently checked in Explorer"),
        })

    assumption_sources = []
    for item in assumption_copies:
        assumption_sources.append({
            "assumption_id": item.get("assumption_id"),
            "key": item.get("key"),
            "evidence_classification": item.get("evidence_classification"),
            "source_reference": item.get("source_reference"),
            "source_level": item.get("source_level"),
            "review_expiry_date": item.get("review_expiry_date"),
            "review_due": _is_review_due(item.get("review_expiry_date"), today),
        })

    classification = adapter_coverage_classification(coverage_id)
    deferred = classification == "unsupported_deferred_coverage"
    return {
        "contract_version": SOURCEMATE_CONTRACT_VERSION,
        "source_module": calculation_copy.get("source_module"),
        "source_function": calculation_copy.get("source_function"),
        "calculation_id": calculation_id,
        "formula_id": calculation_copy.get("formula_id"),
        "formula_version": calculation_copy.get("formula_version"),
        "coverage_id": coverage_id,
        "coverage_classification": classification,
        "authoritative_service_available": True,
        "dedicated_adapter_deferred": deferred,
        "adapter_reconciled": classification == "adapter_backed",
        "assumption_sources": assumption_sources,
        "export_evidence": evidence_rows,
        "evidence_registration_status": "registered" if evidence_rows else "not registered",
        "limitations": list(SOURCEMATE_LIMITATIONS),
        "human_review_required": True,
        "external_verification_claimed": False,
    }
