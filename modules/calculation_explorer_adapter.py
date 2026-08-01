"""Read-only adapter from authoritative engine outputs to explorer payloads.

This module never evaluates formula metadata and never recalculates procurement
results. It only normalizes values already produced by existing engines.
"""

from __future__ import annotations

from dataclasses import asdict

from modules.assumption_provenance import build_assumption_register, provenance_counts
from modules.calculation_catalogue import (
    CALCULATIONS,
    EXCEL_EVIDENCE_MAP,
    HUMAN_REVIEW_BOUNDARY,
    JSON_EVIDENCE_MAP,
)
from modules.calculation_reconciliation import (
    reconcile_annual_value,
    reconcile_component_total,
    reconcile_currency,
)


def _calculation_payload(definition, authoritative_results):
    metadata = asdict(definition)
    result = authoritative_results.get(definition.calculation_id)
    metadata.update(
        {
            "variables": list(metadata["variables"]),
            "downstream_outputs": list(metadata["downstream_outputs"]),
            "result": result,
            "formula_executable": False,
            "excel_evidence": EXCEL_EVIDENCE_MAP.get(definition.calculation_id),
            "json_evidence": JSON_EVIDENCE_MAP.get(definition.calculation_id),
        }
    )
    return metadata


def build_explorer_payload(
    *,
    context,
    assumptions,
    authoritative_results,
    supplied_keys=(),
    inferred_keys=(),
    derived_keys=(),
    reconciliation_inputs=None,
    scenarios=None,
    decision=None,
    allocation=None,
):
    """Return a normalized explorer contract without changing business outputs."""
    register = build_assumption_register(
        assumptions,
        supplied_keys=supplied_keys,
        inferred_keys=inferred_keys,
        derived_keys=derived_keys,
    )
    checks = build_reconciliation_checks(reconciliation_inputs or {})
    return {
        "contract_version": "AIPC-CALC-EXPLORER-1.0",
        "context": dict(context),
        "assumptions": register,
        "provenance_counts": provenance_counts(register),
        "calculations": [
            _calculation_payload(item, authoritative_results)
            for item in CALCULATIONS
            if item.calculation_id in authoritative_results
        ],
        "scenarios": list(scenarios or []),
        "decision": dict(decision or {}),
        "allocation": dict(allocation or {}),
        "reconciliation": checks,
        "export_evidence": {
            "excel": dict(EXCEL_EVIDENCE_MAP),
            "json": dict(JSON_EVIDENCE_MAP),
        },
        "human_review": {
            "required": True,
            "boundary": HUMAN_REVIEW_BOUNDARY,
        },
    }


def build_reconciliation_checks(inputs):
    """Build only checks for evidence supplied by authoritative engines."""
    checks = {}
    for name, result in inputs.get("component_results", {}).items():
        checks[f"components:{name}"] = reconcile_component_total(result)
    for name, values in inputs.get("annual_values", {}).items():
        checks[f"annual:{name}"] = reconcile_annual_value(
            values["unit_value"], values["annual_volume"], values["annual_value"]
        )
    for name, values in inputs.get("currency_values", {}).items():
        checks[f"currency:{name}"] = reconcile_currency(
            values["usd_value"], values["fx_rate"], values["inr_value"]
        )
    return checks


def authoritative_value(payload, calculation_id):
    """Return the exact adapted value; formula metadata is intentionally ignored."""
    for item in payload.get("calculations", []):
        if item["calculation_id"] == calculation_id:
            return item["result"]
    raise KeyError(calculation_id)
