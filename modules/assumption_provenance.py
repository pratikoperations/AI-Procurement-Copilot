"""Deterministic provenance classification for explorer assumptions."""

from __future__ import annotations

from dataclasses import asdict

from modules.calculation_catalogue import ASSUMPTIONS, assumption_by_key


VALID_STATUSES = {"supplied", "defaulted", "inferred", "derived"}


def classify_assumption(key, value, *, supplied_keys=(), inferred_keys=(), derived_keys=()):
    """Return normalized provenance metadata without changing the supplied value."""
    definition = assumption_by_key(key)
    if key in derived_keys:
        status = "derived"
    elif key in inferred_keys:
        status = "inferred"
    elif key in supplied_keys:
        status = "supplied"
    else:
        status = "defaulted"
    payload = {
        "key": key,
        "value": value,
        "status": status,
        "editable": False,
        "edit_scope": "none",
        "unit": "",
        "validation_rules": [],
        "source_module": "unknown",
        "governance_caveat": "Uncatalogued value; human review required.",
    }
    if definition is not None:
        metadata = asdict(definition)
        payload.update(
            {
                "assumption_id": metadata["assumption_id"],
                "business_name": metadata["business_name"],
                "category": metadata["category"],
                "editable": metadata["editable"],
                "edit_scope": metadata["edit_scope"],
                "unit": metadata["unit"],
                "validation_rules": list(metadata["validation_rules"]),
                "source_module": metadata["source_module"],
                "governance_caveat": metadata["governance_caveat"],
            }
        )
    return payload


def build_assumption_register(assumptions, *, supplied_keys=(), inferred_keys=(), derived_keys=()):
    """Build a stable register, preserving uncatalogued values for audit visibility."""
    known_order = [item.key for item in ASSUMPTIONS]
    keys = [key for key in known_order if key in assumptions]
    keys.extend(sorted(key for key in assumptions if key not in set(keys)))
    return [
        classify_assumption(
            key,
            assumptions[key],
            supplied_keys=set(supplied_keys),
            inferred_keys=set(inferred_keys),
            derived_keys=set(derived_keys),
        )
        for key in keys
    ]


def provenance_counts(register):
    counts = {status: 0 for status in sorted(VALID_STATUSES)}
    for item in register:
        status = item["status"]
        if status not in VALID_STATUSES:
            raise ValueError(f"Unsupported provenance status: {status}")
        counts[status] += 1
    return counts
