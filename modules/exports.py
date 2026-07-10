"""Downloadable output helpers for AI Procurement Copilot."""

from io import BytesIO
import json
import pandas as pd


def dataframe_to_csv_bytes(df):
    """Return a dataframe as UTF-8 CSV bytes."""
    return df.to_csv(index=False).encode("utf-8")


def text_to_bytes(text):
    """Return plain text as UTF-8 bytes."""
    return str(text).encode("utf-8")


def build_decision_package_json(
    recommended_supplier,
    value_metrics,
    allocation_df,
    scenario_df,
    negotiation_result,
):
    """Build a compact, machine-readable decision package."""
    payload = {
        "recommended_supplier": recommended_supplier.to_dict()
        if hasattr(recommended_supplier, "to_dict")
        else dict(recommended_supplier),
        "value_metrics": dict(value_metrics),
        "allocation": allocation_df.to_dict(orient="records"),
        "scenarios": scenario_df.to_dict(orient="records"),
        "negotiation": dict(negotiation_result),
    }
    return json.dumps(payload, indent=2, default=str).encode("utf-8")


def build_excel_workbook(scored_df, should_cost_df, allocation_df, scenario_df):
    """Create an in-memory Excel workbook with the core decision outputs."""
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        scored_df.to_excel(writer, sheet_name="Supplier Scores", index=False)
        should_cost_df.to_excel(writer, sheet_name="Should Cost", index=False)
        allocation_df.to_excel(writer, sheet_name="Allocation", index=False)
        scenario_df.to_excel(writer, sheet_name="Scenarios", index=False)
    buffer.seek(0)
    return buffer.getvalue()
