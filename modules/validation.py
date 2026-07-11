"""Validation helpers for RFQ data and procurement engine outputs."""

import pandas as pd

from modules.intelligent_rfq import quality_report_messages

REQUIRED_RFQ_COLUMNS = [
    "Supplier",
    "Quoted Unit Price USD",
    "MOQ",
    "Lead Time Days",
    "Payment Terms",
    "Incoterms",
]

OPTIONAL_RFQ_COLUMNS = [
    "OTIF %",
    "Quality PPM",
    "Audit Score",
    "Complaint Rate %",
    "Capacity Buffer %",
    "Recyclability",
    "Certification",
    "Carbon Score",
    "EPR Readiness",
    "PCR Content %",
    "Supplier Capacity",
]


def validate_rfq_dataframe(df):
    """Return structured validation and intelligent upload diagnostics."""
    errors = []
    warnings = []

    if df is None or df.empty:
        errors.append("RFQ file contains no supplier rows.")
        return {"is_valid": False, "errors": errors, "warnings": warnings, "quality_report": None}

    quality_report = df.attrs.get("rfq_quality_report")
    if quality_report:
        warnings.extend(quality_report_messages(quality_report))

    missing_required = [column for column in REQUIRED_RFQ_COLUMNS if column not in df.columns]
    if missing_required:
        errors.append("Missing required columns after intelligent mapping: " + ", ".join(missing_required))

    if "Supplier" in df.columns:
        supplier_values = df["Supplier"]
        if supplier_values.isna().any() or supplier_values.astype(str).str.strip().eq("").any():
            errors.append("One or more supplier names are blank.")
        duplicate_mask = supplier_values.astype(str).str.strip().str.lower().duplicated(keep=False)
        if duplicate_mask.any():
            names = sorted(supplier_values.loc[duplicate_mask].astype(str).unique().tolist())
            warnings.append("Duplicate supplier entries require review: " + ", ".join(names))

    numeric_rules = {
        "Quoted Unit Price USD": "greater than zero",
        "MOQ": "greater than zero",
        "Lead Time Days": "zero or greater",
    }
    for column, rule in numeric_rules.items():
        if column in df.columns:
            numeric = pd.to_numeric(df[column], errors="coerce")
            if numeric.isna().any():
                errors.append(f"Column '{column}' contains blank or non-numeric values after normalization.")
            elif column == "Lead Time Days" and (numeric < 0).any():
                errors.append(f"Column '{column}' must be {rule}.")
            elif column != "Lead Time Days" and (numeric <= 0).any():
                errors.append(f"Column '{column}' must be {rule}.")

    missing_optional = [column for column in OPTIONAL_RFQ_COLUMNS if column not in df.columns]
    if missing_optional:
        warnings.append(
            "Optional scoring columns are missing and defaults will be used: " + ", ".join(missing_optional)
        )

    if len(df) < 2:
        warnings.append("At least two suppliers are recommended for comparative sourcing analysis.")

    if quality_report and quality_report["quality_score"] < 70:
        warnings.append("RFQ data quality is below 70/100. Review mapping, missing data, and duplicates before award use.")

    return {
        "is_valid": not errors,
        "errors": errors,
        "warnings": list(dict.fromkeys(warnings)),
        "quality_report": quality_report,
    }


def validate_scored_output(scored_df):
    """Validate key outputs after scoring."""
    required_output_columns = [
        "Supplier",
        "adjusted_tco_unit_usd",
        "annual_tco_usd",
        "risk_score",
        "performance_score",
        "esg_score",
        "total_score",
    ]

    errors = [column for column in required_output_columns if column not in scored_df.columns]
    if errors:
        return {
            "is_valid": False,
            "errors": ["Missing scored output columns: " + ", ".join(errors)],
        }

    score_columns = ["risk_score", "performance_score", "esg_score", "total_score"]
    invalid_scores = []
    for column in score_columns:
        if ((scored_df[column] < 0) | (scored_df[column] > 100)).any():
            invalid_scores.append(column)

    messages = []
    if invalid_scores:
        messages.append("Scores outside 0–100 range: " + ", ".join(invalid_scores))

    if (scored_df["adjusted_tco_unit_usd"] <= 0).any():
        messages.append("Adjusted TCO must be greater than zero for every supplier.")

    return {"is_valid": not messages, "errors": messages}
