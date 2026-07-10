"""Validation helpers for RFQ data and procurement engine outputs."""

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
    """Return structured validation results for an uploaded RFQ dataframe."""
    errors = []
    warnings = []

    if df is None or df.empty:
        errors.append("RFQ file contains no supplier rows.")
        return {"is_valid": False, "errors": errors, "warnings": warnings}

    missing_required = [column for column in REQUIRED_RFQ_COLUMNS if column not in df.columns]
    if missing_required:
        errors.append("Missing required columns: " + ", ".join(missing_required))

    if "Supplier" in df.columns and df["Supplier"].astype(str).str.strip().eq("").any():
        errors.append("One or more supplier names are blank.")

    numeric_rules = {
        "Quoted Unit Price USD": "greater than zero",
        "MOQ": "greater than zero",
        "Lead Time Days": "zero or greater",
    }
    for column, rule in numeric_rules.items():
        if column in df.columns:
            numeric = __import__("pandas").to_numeric(df[column], errors="coerce")
            if numeric.isna().any():
                errors.append(f"Column '{column}' contains non-numeric values.")
            elif column == "Lead Time Days" and (numeric < 0).any():
                errors.append(f"Column '{column}' must be {rule}.")
            elif column != "Lead Time Days" and (numeric <= 0).any():
                errors.append(f"Column '{column}' must be {rule}.")

    missing_optional = [column for column in OPTIONAL_RFQ_COLUMNS if column not in df.columns]
    if missing_optional:
        warnings.append(
            "Optional scoring columns are missing and defaults will be used: "
            + ", ".join(missing_optional)
        )

    if len(df) < 2:
        warnings.append("At least two suppliers are recommended for comparative sourcing analysis.")

    return {
        "is_valid": not errors,
        "errors": errors,
        "warnings": warnings,
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
