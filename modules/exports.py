"""Downloadable output helpers for AI Procurement Copilot."""

from io import BytesIO
import json
import pandas as pd


READABLE_SCORE_COLUMNS = {
    "Supplier": "Supplier",
    "Original Currency": "Original Currency",
    "Original Unit Price": "Original Unit Price",
    "Normalized Currency": "Normalized Currency",
    "Normalized Unit Price": "Normalized Unit Price",
    "FX Rate Used": "FX Rate Used",
    "Unit of Measure": "Unit of Measure",
    "Comparison Basis": "Comparison Basis",
    "adjusted_tco_unit_usd": "Risk-Adjusted TCO (USD)",
    "annual_tco_usd": "Annual TCO (USD)",
    "risk_score": "Risk Resilience Score",
    "risk_category": "Risk Category",
    "performance_score": "Performance Score",
    "esg_score": "ESG Score",
    "total_score": "Overall Decision Score",
}


def dataframe_to_csv_bytes(df):
    """Return a dataframe as UTF-8 CSV bytes."""
    return df.to_csv(index=False).encode("utf-8")


def text_to_bytes(text):
    """Return plain text as UTF-8 bytes."""
    return str(text).encode("utf-8")


def build_readable_supplier_scores(scored_df, data_confidence, eligibility):
    """Return a business-readable supplier score report."""
    available = [column for column in READABLE_SCORE_COLUMNS if column in scored_df.columns]
    report = scored_df[available].rename(columns=READABLE_SCORE_COLUMNS).copy()
    report["Data Confidence"] = f"{data_confidence.get('data_confidence_score', 0)}/100 — {data_confidence.get('confidence_category', 'Not assessed')}"
    report["Eligibility Status"] = eligibility.get("status", "Not assessed")
    report["Validation Warning"] = eligibility.get("reason", "")
    report["Human Review Required"] = "Yes"
    return report


def build_readable_supplier_comparison(comparison_df, data_confidence, eligibility):
    """Return a readable supplier-comparison report with governance context."""
    report = comparison_df.copy().rename(columns={"Risk Score": "Risk Resilience Score"})
    report["Data Confidence"] = f"{data_confidence.get('data_confidence_score', 0)}/100 — {data_confidence.get('confidence_category', 'Not assessed')}"
    report["Eligibility Status"] = eligibility.get("status", "Not assessed")
    report["Validation Warning"] = eligibility.get("reason", "")
    report["Human Review Required"] = "Yes"
    return report


def build_decision_package_json(recommended_supplier, value_metrics, allocation_df, scenario_df, negotiation_result, eligibility=None):
    """Build a compact, machine-readable audit package."""
    payload = {
        "recommended_supplier": recommended_supplier.to_dict() if hasattr(recommended_supplier, "to_dict") else dict(recommended_supplier),
        "value_metrics": dict(value_metrics),
        "allocation": allocation_df.to_dict(orient="records"),
        "scenarios": scenario_df.to_dict(orient="records"),
        "negotiation": dict(negotiation_result),
        "eligibility": dict(eligibility or {}),
    }
    return json.dumps(payload, indent=2, default=str).encode("utf-8")


def build_excel_workbook(scored_df, should_cost_df, allocation_df, scenario_df, readable_scores=None, readable_comparison=None):
    """Create an in-memory Excel workbook with readable and audit sheets."""
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        (readable_scores if readable_scores is not None else scored_df).to_excel(writer, sheet_name="Supplier Scores Report", index=False)
        if readable_comparison is not None:
            readable_comparison.to_excel(writer, sheet_name="Supplier Comparison", index=False)
        should_cost_df.to_excel(writer, sheet_name="Should Cost", index=False)
        allocation_df.to_excel(writer, sheet_name="Allocation", index=False)
        scenario_df.to_excel(writer, sheet_name="Scenarios", index=False)
        scored_df.to_excel(writer, sheet_name="Audit Supplier Scores", index=False)
    buffer.seek(0)
    return buffer.getvalue()
