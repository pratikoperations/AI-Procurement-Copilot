"""Cross-engine procurement business-rule validation."""

from __future__ import annotations

import math

import pandas as pd


PERCENTAGE_FIELDS = [
    "OTIF %",
    "Audit Score",
    "Complaint Rate %",
    "Capacity Utilization %",
    "Recyclability",
    "Certification",
    "Carbon Score",
    "EPR Readiness",
    "PCR Content %",
]


def _numeric_series(dataframe: pd.DataFrame, column: str):
    if column not in dataframe.columns:
        return None
    return pd.to_numeric(dataframe[column], errors="coerce")


def validate_business_rules(
    suppliers_df: pd.DataFrame,
    annual_volume: float,
    allocation_df: pd.DataFrame | None = None,
    supplier_profiles: list[dict] | None = None,
    recommendation_status: str | None = None,
) -> dict:
    """Validate critical procurement, allocation, and governance rules."""
    blocking = []
    warnings = []

    if suppliers_df is None or suppliers_df.empty:
        blocking.append("No supplier records are available.")
        return _result(blocking, warnings)

    try:
        volume = float(annual_volume)
    except (TypeError, ValueError):
        volume = math.nan
    if not math.isfinite(volume) or volume <= 0:
        blocking.append("Annual volume must be greater than zero.")

    checks = {
        "Quoted Unit Price USD": (lambda x: x > 0, "Quoted price must be greater than zero."),
        "MOQ": (lambda x: x >= 0, "MOQ must be non-negative."),
        "Lead Time Days": (lambda x: x >= 0, "Lead time must be non-negative."),
        "Supplier Capacity": (lambda x: x >= 0, "Supplier capacity must be non-negative."),
        "Quality PPM": (lambda x: x >= 0, "Quality PPM must be non-negative."),
        "Complaint Rate %": (lambda x: x >= 0, "Complaint rate must be non-negative."),
    }
    for column, (predicate, message) in checks.items():
        series = _numeric_series(suppliers_df, column)
        if series is None:
            continue
        if series.isna().any():
            blocking.append(f"{column} contains blank or non-numeric values.")
        elif not series.map(predicate).all():
            blocking.append(message)

    for column in PERCENTAGE_FIELDS:
        series = _numeric_series(suppliers_df, column)
        if series is None:
            continue
        if series.isna().any():
            warnings.append(f"{column} contains blank or non-numeric values.")
        elif ((series < 0) | (series > 100)).any():
            blocking.append(f"{column} must be between 0 and 100.")
        elif ((series > 0) & (series <= 1)).any():
            warnings.append(f"{column} may contain decimal percentages such as 0.95 instead of 95; confirm the source format.")

    if "Capacity Utilization %" in suppliers_df.columns:
        utilization = _numeric_series(suppliers_df, "Capacity Utilization %")
        if utilization is not None and ((utilization < 0) | (utilization > 100)).any():
            blocking.append("Capacity utilization must be between 0 and 100.")

    currencies = _distinct_nonblank(suppliers_df, "Currency")
    units = _distinct_nonblank(suppliers_df, "Unit")
    if not currencies:
        warnings.append("Currency is not explicitly supplied; uploaded award decisions require confirmation.")
    elif len(currencies) > 1:
        blocking.append("Mixed currencies must be converted to a common comparison currency before recommendation.")
    if not units:
        warnings.append("Unit of measure is not explicitly supplied; uploaded award decisions require confirmation.")
    elif len(units) > 1:
        blocking.append("Mixed units must be normalized before recommendation.")

    if "Supplier" in suppliers_df.columns:
        normalized = suppliers_df["Supplier"].astype(str).str.strip().str.lower()
        if normalized.duplicated(keep=False).any():
            warnings.append("Duplicate supplier names require consolidation or explicit site-level distinction.")

    if "Supplier Capacity" in suppliers_df.columns and math.isfinite(volume) and volume > 0:
        capacity = _numeric_series(suppliers_df, "Supplier Capacity")
        if capacity is not None and not capacity.isna().any() and capacity.sum() < volume:
            blocking.append("Total supplier capacity is below annual demand.")

    if allocation_df is not None and not allocation_df.empty:
        pct_col = "Recommended Allocation %"
        if pct_col not in allocation_df.columns:
            blocking.append("Allocation output does not contain Recommended Allocation %.")
        else:
            total = pd.to_numeric(allocation_df[pct_col], errors="coerce").sum()
            if abs(float(total) - 100.0) > 0.001:
                blocking.append(f"Recommended allocation totals {total:.2f}% instead of 100%.")

        if {"Supplier", pct_col}.issubset(allocation_df.columns) and "Supplier Capacity" in suppliers_df.columns and math.isfinite(volume):
            capacity_map = dict(zip(suppliers_df["Supplier"].astype(str), pd.to_numeric(suppliers_df["Supplier Capacity"], errors="coerce")))
            for _, allocation in allocation_df.iterrows():
                supplier = str(allocation["Supplier"])
                share = float(allocation[pct_col]) / 100
                required = volume * share
                available = capacity_map.get(supplier)
                if available is None or pd.isna(available):
                    warnings.append(f"Capacity is unavailable for allocated supplier {supplier}.")
                elif required > float(available) + 1e-9:
                    blocking.append(f"Allocation to {supplier} requires {required:,.0f} units but capacity is {float(available):,.0f}.")

    if supplier_profiles:
        for profile in supplier_profiles:
            classification = profile.get("srm", {}).get("srm_classification")
            financial_risk = profile.get("financial", {}).get("financial_risk_category")
            if classification == "Strategic" and financial_risk == "Critical":
                blocking.append(f"{profile.get('supplier_name')} cannot be Strategic without a critical financial-risk override and mitigation.")

    if recommendation_status == "Blocked":
        warnings.append("Blocked recommendations must not produce an executive award narrative.")

    return _result(blocking, warnings)


def _distinct_nonblank(dataframe: pd.DataFrame, column: str) -> list[str]:
    if column not in dataframe.columns:
        return []
    values = dataframe[column].dropna().astype(str).str.strip()
    return sorted(value for value in values.unique().tolist() if value)


def _result(blocking: list[str], warnings: list[str]) -> dict:
    blocking = list(dict.fromkeys(blocking))
    warnings = list(dict.fromkeys(warnings))
    status = "Fail" if blocking else "Warning" if warnings else "Pass"
    actions = ["Correct all blocking data or allocation issues before recommendation."] if blocking else []
    if warnings:
        actions.append("Review and document all warnings before approval.")
    if not actions:
        actions.append("Proceed to human procurement review.")
    return {
        "status": status,
        "blocking_issues": blocking,
        "non_blocking_issues": warnings,
        "corrective_action": actions,
    }
