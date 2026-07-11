"""Category-aware supplier scoring engine."""

import pandas as pd

from modules.esg import calculate_esg_score
from modules.performance import calculate_performance_score
from modules.raw_material_tco import calculate_raw_material_tco
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


def enrich_supplier_scores(df, assumptions, weights=None):
    """Add category-specific TCO, risk, ESG, performance, and weighted scores."""
    category = assumptions.get("category", "Packaging Procurement")
    weights = weights or (RAW_MATERIAL_WEIGHTS if category == "Raw Material Procurement" else DEFAULT_WEIGHTS)
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
        record["esg_score"] = calculate_esg_score(record)
        record["performance_score"] = calculate_performance_score(record)
        rows.append(record)

    scored = pd.DataFrame(rows)
    min_tco = safe_positive(scored["adjusted_tco_unit_usd"].min())
    min_moq = safe_positive(scored["MOQ"].min())
    min_lead = safe_positive(scored["Lead Time Days"].min())

    scored["tco_score"] = (min_tco / scored["adjusted_tco_unit_usd"].apply(safe_positive)) * 100
    scored["moq_score"] = (min_moq / scored["MOQ"].apply(safe_positive)) * 100
    scored["lead_time_score"] = (min_lead / scored["Lead Time Days"].apply(safe_positive)) * 100
    scored["payment_score"] = scored["Payment Terms"].astype(str).str.extract(r"(\d+)").fillna(30).astype(float)[0].clip(upper=90) / 90 * 100

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
    return scored.sort_values("total_score", ascending=False).reset_index(drop=True)
