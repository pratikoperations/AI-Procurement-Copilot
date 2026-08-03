"""Downloadable output helpers for AI Procurement Copilot."""

from io import BytesIO
import json
import math

import pandas as pd
import streamlit as st

from modules.unit_display import add_annual_volume_metadata
from modules.utils import build_currency_display_frame, normalize_display_currency

C2_EXPORT_CONTRACT_VERSION = "AIPC-MULTI-ALLOC-EXPORT-1.0"
C2_SCHEMA_MIGRATION_NOTE = (
    "Legacy Standard Allocation, Optimized Allocation and Visible Winner fields were removed because "
    "they no longer represented independent governed authorities after canonical allocation reconciliation."
)
C2_EXPORT_DISCLAIMER = (
    "Synthetic controlled demonstration assumptions only; not audited supplier evidence, laboratory "
    "results, technical certification, market forecast, production-readiness claim or realized savings."
)
READABLE_SCORE_COLUMNS = {
    "Supplier": "Supplier", "Original Currency": "Original Currency", "Original Unit Price": "Original Unit Price",
    "Normalized Currency": "Normalized Currency", "Normalized Unit Price": "Normalized Unit Price",
    "FX Rate Used": "FX Rate Used", "Unit of Measure": "Unit of Measure", "Comparison Basis": "Comparison Basis",
    "Laminate Structure": "Selected Laminate Structure", "Total Micron": "Total Micron (Metadata Only)",
    "technical_eligible": "Technical Eligibility", "technical_ineligibility_reasons": "Technical Ineligibility Reasons",
    "generic_failure_probability": "Generic Failure Probability", "laminate_failure_probability": "Laminate Failure Probability",
    "generic_risk_penalty_usd": "Generic Risk Penalty USD/kg", "laminate_risk_penalty_usd": "Laminate Risk Penalty USD/kg",
    "combined_risk_penalty_usd": "Combined Risk Penalty USD/kg",
    "risk_score": "Risk Resilience Score", "risk_category": "Risk Category", "performance_score": "RFQ Performance Score",
    "esg_score": "RFQ ESG Score", "supplier360_performance_score": "Supplier 360 Performance Score",
    "governed_financial_indicator": "Governed Financial Indicator", "governed_esg_maturity_score": "Governed ESG Maturity Score",
    "governed_innovation_maturity_score": "Governed Innovation Maturity Score", "supplier360_score": "Supplier 360 Score",
    "total_score": "Overall Decision Score",
}
SCENARIO_ANNUAL_TCO_CANDIDATES = ("Annual TCO (USD)", "Annual TCO USD", "annual_tco_usd")
SCENARIO_ALLOCATION_EXPORT_COLUMNS = (
    "Scenario",
    "Scenario Applicable",
    "Scenario Assumption Version",
    "Scenario Route Status",
    "Canonical Allocation Status",
    "Allocation Available",
    "Selected Suppliers",
    "Allocation Shares",
    "Allocated Volumes",
    "Primary Supplier",
    "Continuity Supplier",
    "Evidence Origin",
    "Human Review Required",
    "Legacy Fallback Used",
    "Warnings",
    "Blocking Reasons",
    "Analytical Leading Supplier",
    "Analytical Leading Score",
)
EXPORT_CACHE_MAX_ENTRIES = 16


def dataframe_to_csv_bytes(df):
    return df.to_csv(index=False).encode("utf-8")


def text_to_bytes(text):
    return str(text).encode("utf-8")


def _available_currency_mapping(frame, candidates):
    return {column: label for column, label in candidates.items() if column in frame.columns}


def _drop_existing_inr_columns(frame, labels):
    result = frame.copy()
    removable = set()
    for label in labels:
        removable.update({f"{label} INR", f"{label} (INR)", f"{label}_inr"})
    return result.drop(columns=[column for column in removable if column in result.columns], errors="ignore")


def _is_c2_frame(frame):
    return "Laminate Structure" in frame.columns or "Selected Laminate Structure" in frame.columns


def _add_c2_governance(report):
    result = report.copy()
    result["Commercial Basis"] = "kg"
    result["Comparison Unit"] = "USD/kg"
    result["Confidence Governance"] = "Controlled governance indicator; not predictive accuracy."
    result["Synthetic / Non-Certification Disclaimer"] = C2_EXPORT_DISCLAIMER
    return result


def _normalize_strict_json(value):
    """Recursively convert pandas/NumPy missing and non-finite values to JSON null."""
    if value is None:
        return None
    if isinstance(value, pd.DataFrame):
        return _normalize_strict_json(value.to_dict(orient="records"))
    if isinstance(value, pd.Series):
        return _normalize_strict_json(value.to_list())
    if isinstance(value, dict):
        return {str(key): _normalize_strict_json(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_normalize_strict_json(item) for item in value]
    if isinstance(value, (str, bool, int)):
        return value
    if hasattr(value, "item"):
        try:
            value = value.item()
        except (TypeError, ValueError):
            pass
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    return value


def _scenario_allocation_frame(scenario_df):
    """Project existing Gate 3C2A fields without reconstructing scenario allocation."""
    available = [column for column in SCENARIO_ALLOCATION_EXPORT_COLUMNS if column in scenario_df.columns]
    return scenario_df[available].copy() if available else pd.DataFrame()


@st.cache_data(show_spinner=False, max_entries=EXPORT_CACHE_MAX_ENTRIES)
def build_readable_supplier_scores(scored_df, data_confidence, eligibility, supplier_comparison=None, display_currency="USD", fx_rate=83, annual_volume=None, annual_volume_unit=None):
    mode = normalize_display_currency(display_currency)
    available = [column for column in READABLE_SCORE_COLUMNS if column in scored_df.columns]
    report = scored_df[available].rename(columns=READABLE_SCORE_COLUMNS).copy()
    if "Technical Eligibility" in report.columns:
        report["Technical Eligibility"] = report["Technical Eligibility"].map({True: "Eligible", False: "Ineligible"}).fillna("Not assessed")
    currency_columns = _available_currency_mapping(scored_df, {"adjusted_tco_unit_usd": "Risk-Adjusted TCO", "annual_tco_usd": "Annual TCO"})
    if currency_columns:
        currency_frame = build_currency_display_frame(scored_df[list(currency_columns)].copy(), currency_columns, mode, fx_rate)
        report = pd.concat([report.reset_index(drop=True), currency_frame.reset_index(drop=True)], axis=1)
    if supplier_comparison is not None and not supplier_comparison.empty and "Supplier" in supplier_comparison.columns:
        governed_columns = {"Performance Score": "Supplier 360 Performance Score", "ESG Score": "Governed ESG Maturity Score", "Financial Indicator": "Governed Financial Indicator", "Innovation Score": "Governed Innovation Maturity Score", "Supplier 360 Score": "Supplier 360 Score"}
        available_governed = ["Supplier"] + [column for column in governed_columns if column in supplier_comparison.columns]
        report = report.merge(supplier_comparison[available_governed].rename(columns=governed_columns), on="Supplier", how="left", suffixes=("", " Comparison"))
    report["Data Confidence"] = f"{data_confidence.get('data_confidence_score', 0)}/100 — {data_confidence.get('confidence_category', 'Not assessed')}"
    report["Eligibility Status"] = eligibility.get("status", "Not assessed")
    report["Validation Warning"] = eligibility.get("reason", "")
    report["Human Review Required"] = "Yes"
    if _is_c2_frame(scored_df):
        report = _add_c2_governance(report)
    return add_annual_volume_metadata(report, annual_volume, annual_volume_unit)


@st.cache_data(show_spinner=False, max_entries=EXPORT_CACHE_MAX_ENTRIES)
def build_readable_supplier_comparison(comparison_df, data_confidence, eligibility, display_currency="USD", fx_rate=83, annual_volume=None, annual_volume_unit=None):
    mode = normalize_display_currency(display_currency)
    source = comparison_df.copy()
    currency_columns = _available_currency_mapping(source, {"Risk-Adjusted TCO (USD)": "Risk-Adjusted TCO", "Risk-Adjusted TCO USD": "Risk-Adjusted TCO", "adjusted_tco_unit_usd": "Risk-Adjusted TCO", "Quoted Price USD": "Quoted Price"})
    report = source.drop(columns=list(currency_columns), errors="ignore").rename(columns={"Risk Score": "Risk Resilience Score"})
    if currency_columns:
        report = pd.concat([report.reset_index(drop=True), build_currency_display_frame(source[list(currency_columns)].copy(), currency_columns, mode, fx_rate).reset_index(drop=True)], axis=1)
    report["Data Confidence"] = f"{data_confidence.get('data_confidence_score', 0)}/100 — {data_confidence.get('confidence_category', 'Not assessed')}"
    report["Eligibility Status"] = eligibility.get("status", "Not assessed")
    report["Validation Warning"] = eligibility.get("reason", "")
    report["Human Review Required"] = "Yes"
    return add_annual_volume_metadata(report, annual_volume, annual_volume_unit)


@st.cache_data(show_spinner=False, max_entries=EXPORT_CACHE_MAX_ENTRIES)
def build_readable_allocation(allocation_df, display_currency="USD", fx_rate=83, annual_volume=None, annual_volume_unit=None):
    source = _drop_existing_inr_columns(allocation_df, ["Estimated Annual TCO"])
    mapping = _available_currency_mapping(source, {"Estimated Annual TCO USD": "Estimated Annual TCO", "Estimated Annual TCO (USD)": "Estimated Annual TCO", "annual_tco_usd": "Estimated Annual TCO"})
    report = build_currency_display_frame(source, mapping, display_currency, fx_rate) if mapping else source.copy()
    return add_annual_volume_metadata(report, annual_volume, annual_volume_unit)


@st.cache_data(show_spinner=False, max_entries=EXPORT_CACHE_MAX_ENTRIES)
def build_readable_should_cost(should_cost_df, display_currency="USD", fx_rate=83, annual_volume=None, annual_volume_unit=None):
    source = _drop_existing_inr_columns(should_cost_df, ["Unit Cost", "Annual Impact"])
    mapping = _available_currency_mapping(source, {"Unit Cost USD": "Unit Cost", "Unit Cost (USD)": "Unit Cost", "Annual Impact USD": "Annual Impact", "Annual Impact (USD)": "Annual Impact"})
    report = build_currency_display_frame(source, mapping, display_currency, fx_rate) if mapping else source.copy()
    return add_annual_volume_metadata(report, annual_volume, annual_volume_unit)


@st.cache_data(show_spinner=False, max_entries=EXPORT_CACHE_MAX_ENTRIES)
def build_readable_scenarios(scenario_df, display_currency="USD", fx_rate=83, annual_volume=None, annual_volume_unit=None):
    source = _drop_existing_inr_columns(scenario_df, ["Annual TCO"])
    annual_column = next((column for column in SCENARIO_ANNUAL_TCO_CANDIDATES if column in source.columns), None)
    mapping = {annual_column: "Annual TCO"} if annual_column else {}
    report = build_currency_display_frame(source, mapping, display_currency, fx_rate) if mapping else source.copy()
    if "Scenario Assumption Version" in report.columns:
        report = _add_c2_governance(report)
    return add_annual_volume_metadata(report, annual_volume, annual_volume_unit)


def build_c2_export_manifest(scored_df, canonical_allocation_df, scenario_df, legacy_scenario_df=None):
    """Build the strict-JSON C2 manifest from one canonical allocation authority.

    ``legacy_scenario_df`` temporarily accepts the previous four-argument application
    call shape. The third allocation argument is never serialized or treated as an
    authority; the fourth argument is used only as the scenario dataframe.
    """
    scenario_source = legacy_scenario_df if legacy_scenario_df is not None else scenario_df
    eligible = scored_df[scored_df.get("technical_eligible", False).astype(bool)] if "technical_eligible" in scored_df.columns else scored_df.iloc[0:0]
    analytical_leader = eligible.iloc[0]["Supplier"] if not eligible.empty else "No technically eligible supplier"
    scenario_allocations = _scenario_allocation_frame(scenario_source)
    manifest = {
        "export_contract_version": C2_EXPORT_CONTRACT_VERSION,
        "selected_structure": str(scored_df.iloc[0].get("Laminate Structure", "Not assessed")) if not scored_df.empty else "Not assessed",
        "commercial_basis": "kg",
        "comparison_unit": "USD/kg",
        "analytical_leading_supplier": analytical_leader,
        "eligible_supplier_count": int(len(eligible)),
        "canonical_allocation": canonical_allocation_df.to_dict(orient="records"),
        "scenario_allocations": scenario_allocations.to_dict(orient="records"),
        "scenario_assumption_versions": sorted(set(scenario_source.get("Scenario Assumption Version", pd.Series(dtype=str)).dropna().astype(str))),
        "human_review_required": True,
        "legacy_fallback_used": False,
        "disclaimer": C2_EXPORT_DISCLAIMER,
        "schema_migration_note": C2_SCHEMA_MIGRATION_NOTE,
    }
    return _normalize_strict_json(manifest)


@st.cache_data(show_spinner=False, max_entries=EXPORT_CACHE_MAX_ENTRIES)
def build_decision_package_json(recommended_supplier, value_metrics, allocation_df, scenario_df, negotiation_result, eligibility=None, c2_manifest=None):
    payload = {
        "recommended_supplier": recommended_supplier.to_dict() if hasattr(recommended_supplier, "to_dict") else dict(recommended_supplier),
        "value_metrics": dict(value_metrics),
        "negotiation": dict(negotiation_result),
        "eligibility": dict(eligibility or {}),
    }
    if c2_manifest is None:
        payload["allocation"] = allocation_df.to_dict(orient="records")
        payload["scenarios"] = scenario_df.to_dict(orient="records")
    else:
        payload["canonical_allocation"] = allocation_df.to_dict(orient="records")
        payload["scenarios"] = scenario_df.to_dict(orient="records")
        payload["scenario_allocations"] = list(c2_manifest.get("scenario_allocations", []))
        payload["flexible_laminates_governance"] = dict(c2_manifest)
    normalized_payload = _normalize_strict_json(payload)
    return json.dumps(normalized_payload, indent=2, default=str, allow_nan=False).encode("utf-8")


@st.cache_data(show_spinner=False, max_entries=EXPORT_CACHE_MAX_ENTRIES)
def build_excel_workbook(scored_df, should_cost_df, allocation_df, scenario_df, readable_scores=None, readable_comparison=None, display_currency="USD", fx_rate=83, annual_volume=None, annual_volume_unit=None, optimized_allocation_df=None, c2_manifest=None):
    scores = readable_scores if readable_scores is not None else build_readable_supplier_scores(scored_df, {}, {}, display_currency=display_currency, fx_rate=fx_rate, annual_volume=annual_volume, annual_volume_unit=annual_volume_unit)
    comparison = readable_comparison
    should_cost = build_readable_should_cost(should_cost_df, display_currency, fx_rate, annual_volume, annual_volume_unit)
    allocation = build_readable_allocation(allocation_df, display_currency, fx_rate, annual_volume, annual_volume_unit)
    scenarios = build_readable_scenarios(scenario_df, display_currency, fx_rate, annual_volume, annual_volume_unit)
    scenario_allocations = _scenario_allocation_frame(scenario_df)
    optimized = build_readable_allocation(optimized_allocation_df, display_currency, fx_rate, annual_volume, annual_volume_unit) if optimized_allocation_df is not None else pd.DataFrame()
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        scores.to_excel(writer, sheet_name="Supplier Scores Report", index=False)
        if comparison is not None:
            comparison.to_excel(writer, sheet_name="Supplier Comparison", index=False)
        should_cost.to_excel(writer, sheet_name="Should Cost", index=False)
        if c2_manifest is not None:
            allocation.to_excel(writer, sheet_name="Canonical Allocation", index=False)
            scenarios.to_excel(writer, sheet_name="Scenarios", index=False)
            scenario_allocations.to_excel(writer, sheet_name="Scenario Allocations", index=False)
        else:
            allocation.to_excel(writer, sheet_name="Allocation", index=False)
            if optimized_allocation_df is not None:
                optimized.to_excel(writer, sheet_name="Optimized Allocation", index=False)
            scenarios.to_excel(writer, sheet_name="Scenarios", index=False)
        scored_df.to_excel(writer, sheet_name="Audit Supplier Scores", index=False)
        if c2_manifest is not None:
            pd.DataFrame([
                {
                    "Field": key,
                    "Value": json.dumps(value, default=str, allow_nan=False) if isinstance(value, (list, dict)) else value,
                }
                for key, value in _normalize_strict_json(c2_manifest).items()
            ]).to_excel(writer, sheet_name="C2 Governance", index=False)
    buffer.seek(0)
    return buffer.getvalue()
