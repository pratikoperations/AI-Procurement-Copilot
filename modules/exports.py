"""Downloadable output helpers for AI Procurement Copilot."""

from io import BytesIO
import json

import pandas as pd

from modules.utils import build_currency_display_frame, normalize_display_currency


READABLE_SCORE_COLUMNS = {
    "Supplier": "Supplier",
    "Original Currency": "Original Currency",
    "Original Unit Price": "Original Unit Price",
    "Normalized Currency": "Normalized Currency",
    "Normalized Unit Price": "Normalized Unit Price",
    "FX Rate Used": "FX Rate Used",
    "Unit of Measure": "Unit of Measure",
    "Comparison Basis": "Comparison Basis",
    "risk_score": "Risk Resilience Score",
    "risk_category": "Risk Category",
    "performance_score": "RFQ Performance Score",
    "esg_score": "RFQ ESG Score",
    "supplier360_performance_score": "Supplier 360 Performance Score",
    "governed_financial_indicator": "Governed Financial Indicator",
    "governed_esg_maturity_score": "Governed ESG Maturity Score",
    "governed_innovation_maturity_score": "Governed Innovation Maturity Score",
    "supplier360_score": "Supplier 360 Score",
    "total_score": "Overall Decision Score",
}


SCENARIO_ANNUAL_TCO_CANDIDATES = (
    "Annual TCO (USD)",
    "Annual TCO USD",
    "annual_tco_usd",
)


def dataframe_to_csv_bytes(df):
    """Return a dataframe as UTF-8 CSV bytes."""
    return df.to_csv(index=False).encode("utf-8")


def text_to_bytes(text):
    """Return plain text as UTF-8 bytes."""
    return str(text).encode("utf-8")


def _available_currency_mapping(frame, candidates):
    """Return only governed currency columns that exist in a frame."""
    return {column: label for column, label in candidates.items() if column in frame.columns}


def _drop_existing_inr_columns(frame, labels):
    """Remove precomputed display-INR columns so conversion happens once."""
    result = frame.copy()
    removable = set()
    for label in labels:
        removable.update({f"{label} INR", f"{label} (INR)", f"{label}_inr"})
    return result.drop(columns=[column for column in removable if column in result.columns], errors="ignore")


def build_readable_supplier_scores(
    scored_df,
    data_confidence,
    eligibility,
    supplier_comparison=None,
    display_currency="USD",
    fx_rate=83,
):
    """Return a business-readable score report with governed display currency."""
    mode = normalize_display_currency(display_currency)
    available = [column for column in READABLE_SCORE_COLUMNS if column in scored_df.columns]
    report = scored_df[available].rename(columns=READABLE_SCORE_COLUMNS).copy()

    currency_columns = _available_currency_mapping(scored_df, {
        "adjusted_tco_unit_usd": "Risk-Adjusted TCO",
        "annual_tco_usd": "Annual TCO",
    })
    if currency_columns:
        currency_frame = build_currency_display_frame(
            scored_df[list(currency_columns)].copy(), currency_columns, mode, fx_rate
        )
        report = pd.concat([report.reset_index(drop=True), currency_frame.reset_index(drop=True)], axis=1)

    if supplier_comparison is not None and not supplier_comparison.empty and "Supplier" in supplier_comparison.columns:
        governed_columns = {
            "Performance Score": "Supplier 360 Performance Score",
            "ESG Score": "Governed ESG Maturity Score",
            "Financial Indicator": "Governed Financial Indicator",
            "Innovation Score": "Governed Innovation Maturity Score",
            "Supplier 360 Score": "Supplier 360 Score",
        }
        available_governed = ["Supplier"] + [column for column in governed_columns if column in supplier_comparison.columns]
        governed = supplier_comparison[available_governed].rename(columns=governed_columns).copy()
        report = report.merge(governed, on="Supplier", how="left", suffixes=("", " Comparison"))

    report["Data Confidence"] = f"{data_confidence.get('data_confidence_score', 0)}/100 — {data_confidence.get('confidence_category', 'Not assessed')}"
    report["Eligibility Status"] = eligibility.get("status", "Not assessed")
    report["Validation Warning"] = eligibility.get("reason", "")
    report["Human Review Required"] = "Yes"
    return report


def build_readable_supplier_comparison(
    comparison_df,
    data_confidence,
    eligibility,
    display_currency="USD",
    fx_rate=83,
):
    """Return a readable supplier-comparison report with governed display currency."""
    mode = normalize_display_currency(display_currency)
    source = comparison_df.copy()
    currency_columns = _available_currency_mapping(source, {
        "Risk-Adjusted TCO (USD)": "Risk-Adjusted TCO",
        "Risk-Adjusted TCO USD": "Risk-Adjusted TCO",
        "adjusted_tco_unit_usd": "Risk-Adjusted TCO",
        "Quoted Price USD": "Quoted Price",
    })
    report = source.drop(columns=list(currency_columns), errors="ignore").rename(
        columns={"Risk Score": "Risk Resilience Score"}
    )
    if currency_columns:
        currency_frame = build_currency_display_frame(
            source[list(currency_columns)].copy(), currency_columns, mode, fx_rate
        )
        report = pd.concat([report.reset_index(drop=True), currency_frame.reset_index(drop=True)], axis=1)
    report["Data Confidence"] = f"{data_confidence.get('data_confidence_score', 0)}/100 — {data_confidence.get('confidence_category', 'Not assessed')}"
    report["Eligibility Status"] = eligibility.get("status", "Not assessed")
    report["Validation Warning"] = eligibility.get("reason", "")
    report["Human Review Required"] = "Yes"
    return report


def build_readable_allocation(allocation_df, display_currency="USD", fx_rate=83):
    """Return an allocation report using the selected display currency."""
    source = _drop_existing_inr_columns(allocation_df, ["Estimated Annual TCO"])
    mapping = _available_currency_mapping(source, {
        "Estimated Annual TCO USD": "Estimated Annual TCO",
        "Estimated Annual TCO (USD)": "Estimated Annual TCO",
        "annual_tco_usd": "Estimated Annual TCO",
    })
    return build_currency_display_frame(source, mapping, display_currency, fx_rate) if mapping else source.copy()


def build_readable_should_cost(should_cost_df, display_currency="USD", fx_rate=83):
    """Return a should-cost report using the selected display currency."""
    source = _drop_existing_inr_columns(should_cost_df, ["Unit Cost", "Annual Impact"])
    mapping = _available_currency_mapping(source, {
        "Unit Cost USD": "Unit Cost",
        "Unit Cost (USD)": "Unit Cost",
        "Annual Impact USD": "Annual Impact",
        "Annual Impact (USD)": "Annual Impact",
    })
    return build_currency_display_frame(source, mapping, display_currency, fx_rate) if mapping else source.copy()


def build_readable_scenarios(scenario_df, display_currency="USD", fx_rate=83):
    """Return scenario results using the selected display currency."""
    source = _drop_existing_inr_columns(scenario_df, ["Annual TCO"])
    annual_column = next((column for column in SCENARIO_ANNUAL_TCO_CANDIDATES if column in source.columns), None)
    mapping = {annual_column: "Annual TCO"} if annual_column else {}
    return build_currency_display_frame(source, mapping, display_currency, fx_rate) if mapping else source.copy()


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


def build_excel_workbook(
    scored_df,
    should_cost_df,
    allocation_df,
    scenario_df,
    readable_scores=None,
    readable_comparison=None,
    display_currency="USD",
    fx_rate=83,
):
    """Create an Excel workbook with readable sheets and a canonical USD audit sheet."""
    scores = readable_scores if readable_scores is not None else build_readable_supplier_scores(
        scored_df, {}, {}, display_currency=display_currency, fx_rate=fx_rate
    )
    comparison = readable_comparison
    should_cost = build_readable_should_cost(should_cost_df, display_currency, fx_rate)
    allocation = build_readable_allocation(allocation_df, display_currency, fx_rate)
    scenarios = build_readable_scenarios(scenario_df, display_currency, fx_rate)

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        scores.to_excel(writer, sheet_name="Supplier Scores Report", index=False)
        if comparison is not None:
            comparison.to_excel(writer, sheet_name="Supplier Comparison", index=False)
        should_cost.to_excel(writer, sheet_name="Should Cost", index=False)
        allocation.to_excel(writer, sheet_name="Allocation", index=False)
        scenarios.to_excel(writer, sheet_name="Scenarios", index=False)
        scored_df.to_excel(writer, sheet_name="Audit Supplier Scores", index=False)
    buffer.seek(0)
    return buffer.getvalue()
