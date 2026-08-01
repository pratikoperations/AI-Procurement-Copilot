"""Deterministic, evidence-aware provenance metadata for explorer assumptions."""
from __future__ import annotations
from dataclasses import asdict

from modules.calculation_catalogue import ASSUMPTIONS, UNDOCUMENTED_DEFAULT, assumption_by_key
from modules.parameter_profile_records import EVIDENCE_CLASSIFICATIONS

VALID_STATUSES = {"supplied", "defaulted", "inferred", "derived"}


def classify_assumption(key, value, *, supplied_keys=(), inferred_keys=(), derived_keys=(), evidence_overrides=None):
    """Preserve the value and disclose provenance without fabricating evidence."""
    definition = assumption_by_key(key)
    status = "derived" if key in derived_keys else "inferred" if key in inferred_keys else "supplied" if key in supplied_keys else "defaulted"
    evidence_overrides = evidence_overrides or {}
    payload = {
        "key": key, "value": value, "status": status, "assumption_id": None,
        "business_name": key, "category": "Uncatalogued", "editable": False,
        "edit_scope": "none", "unit": "", "original_unit": None,
        "validation_rules": [], "source_module": "unknown", "source_level": "unknown",
        "evidence_classification": UNDOCUMENTED_DEFAULT, "source_reference": None,
        "effective_date": None, "review_expiry_date": None, "confidence": None,
        "override_status": "not_overridden", "override_reason": None,
        "approver": None, "version": "1.0",
        "governance_caveat": "Uncatalogued value; human review required.",
    }
    if definition is not None:
        metadata = asdict(definition)
        payload.update(metadata)
        payload["validation_rules"] = list(metadata["validation_rules"])
        payload["value"] = value
        payload["status"] = status
    override = evidence_overrides.get(key, {})
    if override:
        classification = override.get("evidence_classification", payload["evidence_classification"])
        if classification not in EVIDENCE_CLASSIFICATIONS:
            raise ValueError(f"Unsupported evidence classification: {classification}")
        for field in ("evidence_classification", "source_reference", "effective_date", "review_expiry_date", "confidence", "override_status", "override_reason", "approver", "source_level"):
            if field in override:
                payload[field] = override[field]
    return payload


def build_assumption_register(assumptions, *, supplied_keys=(), inferred_keys=(), derived_keys=(), evidence_overrides=None):
    """Build a stable register, retaining uncatalogued values as read-only evidence."""
    known_order = [item.key for item in ASSUMPTIONS]
    keys = [key for key in known_order if key in assumptions]
    keys.extend(sorted(key for key in assumptions if key not in set(keys)))
    return [classify_assumption(key, assumptions[key], supplied_keys=set(supplied_keys), inferred_keys=set(inferred_keys), derived_keys=set(derived_keys), evidence_overrides=evidence_overrides) for key in keys]


def provenance_counts(register):
    counts = {status: 0 for status in sorted(VALID_STATUSES)}
    for item in register:
        status = item["status"]
        if status not in VALID_STATUSES:
            raise ValueError(f"Unsupported provenance status: {status}")
        counts[status] += 1
    return counts
