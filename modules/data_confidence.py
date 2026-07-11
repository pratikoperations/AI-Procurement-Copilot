"""Data completeness and reliability scoring for procurement recommendations."""

from __future__ import annotations

from typing import Iterable

import pandas as pd

CRITICAL_FIELDS = [
    "Supplier",
    "Quoted Unit Price USD",
    "MOQ",
    "Lead Time Days",
    "Payment Terms",
    "Incoterms",
]

IMPORTANT_FIELDS = [
    "Currency",
    "Unit",
    "OTIF %",
    "Quality PPM",
    "Audit Score",
    "Complaint Rate %",
    "Capacity Buffer %",
    "Supplier Capacity",
]

# Supplier 360 introduces descriptive and governance fields beyond the RFQ schema.
# This denominator prevents those transparent defaults from overwhelming otherwise
# usable RFQ completeness while still applying a material confidence penalty.
EXTENDED_GOVERNANCE_FIELD_ALLOWANCE = 20


def _is_present(value) -> bool:
    if value is None:
        return False
    try:
        if pd.isna(value):
            return False
    except (TypeError, ValueError):
        pass
    return str(value).strip() != ""


def calculate_data_confidence(
    dataframe: pd.DataFrame,
    defaulted_fields: Iterable[str] | None = None,
    inferred_fields: Iterable[str] | None = None,
    source_label: str = "Uploaded supplier data",
) -> dict:
    """Return a transparent completeness score, not a correctness probability."""
    defaulted = set(defaulted_fields or [])
    inferred = set(inferred_fields or [])

    if dataframe is None or dataframe.empty:
        return {
            "actual_supplied_data_percentage": 0.0,
            "defaulted_data_percentage": 0.0,
            "missing_critical_data_percentage": 100.0,
            "inferred_data_percentage": 0.0,
            "data_confidence_score": 0.0,
            "confidence_category": "Insufficient Data",
            "recommendation_warning": "No supplier rows are available.",
            "source_label": source_label,
            "explanation": "This score measures data completeness and reliability, not the probability that a recommendation is correct.",
        }

    considered = list(dict.fromkeys(CRITICAL_FIELDS + IMPORTANT_FIELDS))
    total_cells = max(len(dataframe) * len(considered), 1)
    actual_cells = 0
    missing_critical_cells = 0

    for field in considered:
        if field not in dataframe.columns:
            if field in CRITICAL_FIELDS:
                missing_critical_cells += len(dataframe)
            continue
        for value in dataframe[field].tolist():
            if _is_present(value):
                actual_cells += 1
            elif field in CRITICAL_FIELDS:
                missing_critical_cells += 1

    actual_pct = actual_cells / total_cells * 100
    governance_denominator = len(considered) + EXTENDED_GOVERNANCE_FIELD_ALLOWANCE
    defaulted_pct = min(len(defaulted) / max(governance_denominator, 1) * 100, 100)
    inferred_pct = min(len(inferred) / max(governance_denominator, 1) * 100, 100)
    missing_critical_pct = missing_critical_cells / max(len(dataframe) * len(CRITICAL_FIELDS), 1) * 100

    score = actual_pct - defaulted_pct * 0.35 - inferred_pct * 0.20 - missing_critical_pct * 0.80
    score = round(max(0.0, min(100.0, score)), 1)

    if score >= 85:
        category = "High Confidence"
    elif score >= 70:
        category = "Acceptable With Review"
    elif score >= 50:
        category = "Limited Confidence"
    else:
        category = "Insufficient Data"

    warning = {
        "High Confidence": "Data completeness is strong; human review remains mandatory.",
        "Acceptable With Review": "Some fields are missing, defaulted, or inferred. Review conditions before award.",
        "Limited Confidence": "The recommendation should be treated as provisional and requires human review.",
        "Insufficient Data": "Do not issue a final award recommendation until critical data gaps are closed.",
    }[category]

    return {
        "actual_supplied_data_percentage": round(actual_pct, 1),
        "defaulted_data_percentage": round(defaulted_pct, 1),
        "missing_critical_data_percentage": round(missing_critical_pct, 1),
        "inferred_data_percentage": round(inferred_pct, 1),
        "data_confidence_score": score,
        "confidence_category": category,
        "recommendation_warning": warning,
        "source_label": source_label,
        "defaulted_fields": sorted(defaulted),
        "inferred_fields": sorted(inferred),
        "explanation": "This score measures data completeness and reliability, not the statistical probability that a recommendation is correct.",
    }
