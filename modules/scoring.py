"""Category-aware supplier scoring engine."""

import pandas as pd
from streamlit.runtime.scriptrunner import get_script_run_ctx

from modules.esg import calculate_esg_score
from modules.flexible_laminate_risk import apply_flexible_laminate_risk_to_tco
from modules.hosted_readiness_ui import apply_hosted_readiness_overrides
from modules.performance import calculate_performance_score
from modules.raw_material_tco import calculate_raw_material_tco
from modules.steel_risk import score_and_recommend_steel_suppliers
from modules.tco import calculate_supplier_tco
from modules.utils import safe_positive

DEFAULT_WEIGHTS = {
    "tco": 0.40,
    "risk": 0.20,
    "lead_time": 0.10,
    "payment": 0.08,
    "moq": 0.07,
    "performance": 0.10,
    "esg": 0.05,
}
RAW_MATERIAL_WEIGHTS = {
    "tco": 0.38,
    "risk": 0.27,
    "lead_time": 0.08,
    "payment": 0.07,
    "moq": 0.05,
    "performance": 0.10,
    "esg": 0.05,
}


def _is_steel_route(assumptions):
    return (
        assumptions.get("category") == "Raw Material Procurement"
        and assumptions.get("commodity") == "Steel"
    )


def _in_streamlit_runtime() -> bool:
    """Return True only for an active Streamlit script execution context."""
    return get_script_run_ctx(suppress_warning=True) is not None


def _dispatch_steel_governed_route(df, assumptions):
    """Render and terminate the isolated Steel route before generic scoring."""
    apply_hosted_readiness_overrides()
    from modules.steel_ux import render_steel_governed_dashboard

    render_steel_governed_dashboard(df, assumptions)
    raise RuntimeError("Steel governed route returned without terminating the Streamlit run.")


def _enrich_steel_scores(df, assumptions):
    """Adapt governed C3 Steel scores to the stable analytical score contract."""
    profile = assumptions.get("steel_profile", "CR_COIL_COMMERCIAL")
    display = assumptions.get("display_currency", "Both")
    scored, recommendation = score_and_recommend_steel_suppliers(
        df,
        profile,
        assumptions["annual_volume"],
        assumptions["fx_rate"],
        display,
        substitution_status=assumptions.get("steel_substitution_status", "Not applicable"),
        substitution_requested=assumptions.get("steel_substitution_status", "Not applicable") != "Not applicable",
    )
    scored["Quoted Unit Price USD"] = scored["normalized_usd_per_kg"]
    scored["scenario_unit_price_usd"] = scored["normalized_usd_per_kg"]
    scored["adjusted_tco_unit_usd"] = scored["normalized_usd_per_kg"]
    scored["annual_tco_usd"] = scored["normalized_usd_per_kg"] * float(assumptions["annual_volume"])
    scored["risk_score"] = 100.0 - scored["steel_risk_score"]
    scored["risk_category"] = scored["steel_risk_band"]
    scored["total_score"] = scored["governed_total_score"]
    scored["esg_score"] = scored.apply(lambda row: calculate_esg_score(row.to_dict()), axis=1)
    scored["category_engine"] = "Raw Material Procurement"
    scored.attrs["steel_recommendation"] = recommendation
    scored.attrs["steel_governed_path"] = True
    return scored


def enrich_supplier_scores(df, assumptions, weights=None):
    """Add category-specific TCO, risk, ESG, performance, and weighted scores."""
    category = assumptions.get("category", "Packaging Procurement")
    commodity = assumptions.get("commodity", "Corrugated Board")
    if _is_steel_route(assumptions):
        if _in_streamlit_runtime():
            _dispatch_steel_governed_route(df, assumptions)
        return _enrich_steel_scores(df, assumptions)

    weights = weights or (
        RAW_MATERIAL_WEIGHTS if category == "Raw Material Procurement" else DEFAULT_WEIGHTS
    )
    rows = []

    for _, row in df.iterrows():
        record = row.to_dict()
        if category == "Raw Material Procurement":
            tco = calculate_raw_material_tco(
                record,
                annual_volume=assumptions["annual_volume"],
                commodity_shock=assumptions["raw_material_shock"],
                freight_shock=assumptions["freight_shock"],
                demand_change=assumptions["demand_change"],
            )
        else:
            tco = calculate_supplier_tco(
                record,
                annual_volume=assumptions["annual_volume"],
                raw_material_shock=assumptions["raw_material_shock"],
                freight_shock=assumptions["freight_shock"],
                demand_change=assumptions["demand_change"],
            )
        record.update(tco)
        if category == "Packaging Procurement" and commodity == "Flexible Laminates":
            record.update(
                apply_flexible_laminate_risk_to_tco(
                    record,
                    assumptions["annual_volume"],
                    demand_change=assumptions.get("demand_change", 0.0),
                )
            )
        record["esg_score"] = calculate_esg_score(record)
        record["performance_score"] = calculate_performance_score(record)
        rows.append(record)

    scored = pd.DataFrame(rows)
    min_tco = safe_positive(scored["adjusted_tco_unit_usd"].min())
    min_moq = safe_positive(scored["MOQ"].min())
    min_lead = safe_positive(scored["Lead Time Days"].min())
    scored["tco_score"] = (
        min_tco / scored["adjusted_tco_unit_usd"].apply(safe_positive)
    ) * 100
    scored["moq_score"] = (min_moq / scored["MOQ"].apply(safe_positive)) * 100
    scored["lead_time_score"] = (
        min_lead / scored["Lead Time Days"].apply(safe_positive)
    ) * 100
    scored["payment_score"] = (
        scored["Payment Terms"]
        .astype(str)
        .str.extract(r"(\d+)")
        .fillna(30)
        .astype(float)[0]
        .clip(upper=90)
        / 90
        * 100
    )
    scored["total_score"] = (
        scored["tco_score"] * weights["tco"]
        + scored["risk_score"] * weights["risk"]
        + scored["lead_time_score"] * weights["lead_time"]
        + scored["payment_score"] * weights["payment"]
        + scored["moq_score"] * weights["moq"]
        + scored["performance_score"] * weights["performance"]
        + scored["esg_score"] * weights["esg"]
    ).round(1)
    scored["category_engine"] = category
    if "technical_eligible" not in scored.columns:
        scored["technical_eligible"] = True
    return scored.sort_values(
        ["technical_eligible", "total_score"],
        ascending=[False, False],
    ).reset_index(drop=True)
