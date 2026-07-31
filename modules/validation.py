"""Validation helpers for RFQ data and procurement engine outputs."""

import pandas as pd

from modules.flexible_laminate_validation import validate_flexible_laminate_dataframe
from modules.intelligent_rfq import quality_report_messages
from modules.kraft_paper_validation import validate_kraft_paper_dataframe

REQUIRED_RFQ_COLUMNS = ["Supplier", "Quoted Unit Price USD", "MOQ", "Lead Time Days", "Payment Terms", "Incoterms"]
OPTIONAL_RFQ_COLUMNS = ["OTIF %", "Quality PPM", "Audit Score", "Complaint Rate %", "Capacity Buffer %", "Recyclability", "Certification", "Carbon Score", "EPR Readiness", "PCR Content %", "Supplier Capacity"]


def validate_rfq_dataframe(df, category=None, commodity=None):
    """Return structured validation and category-aware upload diagnostics."""
    errors, warnings = [], []
    if df is None or df.empty:
        errors.append("No supplier quotations are available for analysis. Add a header row and at least one supplier quotation, then upload the RFQ again.")
        return {"is_valid": False, "errors": errors, "warnings": warnings, "quality_report": None}

    quality_report = df.attrs.get("rfq_quality_report")
    if quality_report:
        warnings.extend(quality_report_messages(quality_report))

    missing_required = [column for column in REQUIRED_RFQ_COLUMNS if column not in df.columns]
    if missing_required:
        errors.append("Missing required columns after intelligent mapping: " + ", ".join(missing_required) + ". These are mandatory RFQ fields. Add the columns or rename the source headers clearly, then upload the file again.")

    if "Supplier" in df.columns:
        supplier_values = df["Supplier"]
        if supplier_values.isna().any() or supplier_values.astype(str).str.strip().eq("").any():
            errors.append("One or more supplier names are blank. Complete every supplier-name cell before continuing.")
        duplicate_mask = supplier_values.astype(str).str.strip().str.lower().duplicated(keep=False)
        if duplicate_mask.any():
            names = sorted(supplier_values.loc[duplicate_mask].astype(str).unique().tolist())
            warnings.append("Duplicate supplier entries require review: " + ", ".join(names) + ". Confirm whether these are separate bids or duplicate rows before award use.")

    numeric_rules = {"Quoted Unit Price USD": "greater than zero", "MOQ": "greater than zero", "Lead Time Days": "zero or greater"}
    for column, rule in numeric_rules.items():
        if column in df.columns:
            numeric = pd.to_numeric(df[column], errors="coerce")
            if numeric.isna().any():
                errors.append(f"'{column}' contains blank or non-numeric values. Enter a valid number in every supplier row and upload the RFQ again.")
            elif column == "Lead Time Days" and (numeric < 0).any():
                errors.append(f"'{column}' must be {rule}. Correct the affected supplier row before continuing.")
            elif column != "Lead Time Days" and (numeric <= 0).any():
                errors.append(f"'{column}' must be {rule}. Correct the affected supplier row before continuing.")

    missing_optional = [column for column in OPTIONAL_RFQ_COLUMNS if column not in df.columns]
    if missing_optional:
        warnings.append("Optional scoring fields are missing, so governed defaults will be used: " + ", ".join(missing_optional) + ". Add them for stronger data confidence; the current analysis remains provisional.")
    if len(df) < 2:
        warnings.append("Only one supplier quotation is available. Add at least one more supplier for a meaningful comparative sourcing analysis.")
    if quality_report and quality_report["quality_score"] < 70:
        warnings.append("RFQ data quality is below 70/100. Review column mapping, missing values and duplicate rows before relying on the analysis for an award decision.")

    selected_category = category or df.attrs.get("category")
    selected_commodity = commodity or df.attrs.get("commodity")
    material_values = df["Material"].astype(str).str.strip() if "Material" in df.columns else None

    kraft_selected = selected_category == "Raw Material Procurement" and selected_commodity == "Kraft Paper"
    kraft_present = material_values is not None and material_values.eq("Kraft Paper").any()
    if kraft_selected or kraft_present:
        if selected_commodity and selected_commodity != "Kraft Paper":
            errors.append("Selected commodity conflicts with Kraft Paper supplier data. Correct the commodity selection or Material values before continuing.")
        result = validate_kraft_paper_dataframe(df)
        errors.extend(result["errors"]); warnings.extend(result["warnings"])

    laminate_selected = selected_category == "Packaging Procurement" and selected_commodity == "Flexible Laminates"
    laminate_present = material_values is not None and material_values.eq("Flexible Laminates").any()
    if laminate_selected or laminate_present:
        if selected_category and selected_category != "Packaging Procurement":
            errors.append("Flexible Laminates supplier data must be routed through Packaging Procurement.")
        if selected_commodity and selected_commodity != "Flexible Laminates":
            errors.append("Selected commodity conflicts with Flexible Laminates supplier data.")
        result = validate_flexible_laminate_dataframe(df)
        errors.extend(result["errors"]); warnings.extend(result["warnings"])

    return {"is_valid": not errors, "errors": list(dict.fromkeys(errors)), "warnings": list(dict.fromkeys(warnings)), "quality_report": quality_report}


def validate_scored_output(scored_df):
    """Validate key outputs after scoring."""
    required_output_columns = ["Supplier", "adjusted_tco_unit_usd", "annual_tco_usd", "risk_score", "performance_score", "esg_score", "total_score"]
    errors = [column for column in required_output_columns if column not in scored_df.columns]
    if errors:
        return {"is_valid": False, "errors": ["The scored output is incomplete and cannot support a recommendation. Missing fields: " + ", ".join(errors) + ". Re-run the analysis after correcting the RFQ inputs."]}
    invalid_scores = [column for column in ["risk_score", "performance_score", "esg_score", "total_score"] if ((scored_df[column] < 0) | (scored_df[column] > 100)).any()]
    messages = []
    if invalid_scores:
        messages.append("The following scored fields fall outside the permitted 0–100 range: " + ", ".join(invalid_scores) + ". The recommendation is blocked until the scoring output is corrected.")
    if (scored_df["adjusted_tco_unit_usd"] <= 0).any():
        messages.append("Adjusted TCO must be greater than zero for every supplier. Review price and cost inputs before continuing.")
    if "technical_eligible" in scored_df.columns and not scored_df["technical_eligible"].astype(bool).any():
        messages.append("No technically eligible supplier remains after category-specific risk controls. The recommendation is blocked pending technical review.")
    return {"is_valid": not messages, "errors": messages}
