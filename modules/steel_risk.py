"""Governed C3.4 Steel risk, scoring and recommendation decision path.

All assumptions are controlled synthetic demonstration inputs. This module does not
provide live market intelligence, technical certification, autonomous award or
production readiness.
"""

from __future__ import annotations

import math
from typing import Mapping

import pandas as pd

from modules.steel_cost import normalize_steel_supplier_quotation
from modules.steel_validation import evaluate_steel_supplier_table

STEEL_RISK_WEIGHTS = {
    "steel_index_volatility": 0.10,
    "ore_or_scrap_exposure": 0.06,
    "energy_exposure": 0.07,
    "mill_allocation": 0.09,
    "import_dependency": 0.09,
    "fx_exposure": 0.07,
    "duty_exposure": 0.05,
    "grade_substitution_dependency": 0.06,
    "coating_line_dependency": 0.06,
    "paint_line_dependency": 0.06,
    "source_concentration": 0.07,
    "capacity_utilisation": 0.08,
    "coil_weight_mismatch": 0.05,
    "quality_continuity": 0.05,
    "delivery_continuity": 0.04,
}

DEFAULT_STEEL_RISK_ASSUMPTIONS = {
    "steel_index_volatility_pct": 20.0,
    "ore_or_scrap_exposure_pct": 55.0,
    "energy_exposure_pct": 45.0,
    "fx_exposure_pct": 0.0,
    "duty_exposure_pct": 0.0,
    "grade_substitution_dependency_pct": 0.0,
    "coating_line_dependency_pct": 0.0,
    "paint_line_dependency_pct": 0.0,
}

STEEL_SCORE_WEIGHTS = {
    "commercial": 0.55,
    "generic_risk_fitness": 0.15,
    "steel_risk_fitness": 0.20,
    "performance": 0.10,
}


def _finite(value, label: str, minimum: float = 0.0, maximum: float = 100.0) -> float:
    if value is None or isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a finite numeric value.")
    result = float(value)
    if not math.isfinite(result) or not minimum <= result <= maximum:
        raise ValueError(f"{label} must be within {minimum} and {maximum}.")
    return result


def _risk_band(score: float) -> str:
    if score < 35:
        return "Low"
    if score < 65:
        return "Medium"
    return "High"


def _threshold_risk(value: float, low: float, high: float) -> float:
    """Map controlled evidence onto 0/50/100 risk at explicit thresholds."""
    if value <= low:
        return 0.0
    if value <= high:
        return 50.0
    return 100.0


def calculate_generic_supplier_risk(record: Mapping) -> dict:
    """Return generic supplier risk separately from Steel-specific risk."""
    required = ("OTIF %", "Quality PPM", "Audit Score", "Complaint Rate %", "Risk Category")
    missing = [field for field in required if field not in record or pd.isna(record.get(field))]
    if missing:
        raise ValueError(f"Missing generic risk evidence: {', '.join(missing)}")
    otif = _finite(record["OTIF %"], "OTIF %")
    audit = _finite(record["Audit Score"], "Audit Score")
    complaints = _finite(record["Complaint Rate %"], "Complaint Rate %")
    ppm = _finite(record["Quality PPM"], "Quality PPM", 0.0, 1_000_000.0)
    declared = str(record["Risk Category"]).strip().casefold()
    declared_map = {"low": 15.0, "medium": 50.0, "high": 85.0}
    if declared not in declared_map:
        raise ValueError("Risk Category must be Low, Medium or High.")
    dimensions = {
        "declared_risk": declared_map[declared],
        "otif_risk": 100.0 - otif,
        "quality_ppm_risk": min(100.0, ppm / 20.0),
        "audit_risk": 100.0 - audit,
        "complaint_risk": min(100.0, complaints * 20.0),
    }
    score = round(sum(dimensions.values()) / len(dimensions), 2)
    return {"generic_risk_score": score, "generic_risk_band": _risk_band(score), "generic_risk_dimensions": dimensions}


def calculate_steel_specific_risk(record: Mapping, profile_id: str, assumptions: Mapping | None = None) -> dict:
    """Calculate all 15 frozen Steel-specific dimensions on a 0-100 risk scale."""
    controlled = dict(DEFAULT_STEEL_RISK_ASSUMPTIONS)
    if assumptions:
        controlled.update(assumptions)
    for key in DEFAULT_STEEL_RISK_ASSUMPTIONS:
        controlled[key] = _finite(controlled.get(key), key)

    required = (
        "Mill Allocation %", "Import Dependency %", "Supplier Concentration %",
        "Capacity Utilisation %", "Quality Continuity Score", "OTIF %",
        "Coil Weight Min MT", "Coil Weight Max MT",
    )
    missing = [field for field in required if field not in record or pd.isna(record.get(field))]
    if missing:
        raise ValueError(f"Missing Steel risk evidence: {', '.join(missing)}")

    mill = _finite(record["Mill Allocation %"], "Mill Allocation %")
    imports = _finite(record["Import Dependency %"], "Import Dependency %")
    concentration = _finite(record["Supplier Concentration %"], "Supplier Concentration %")
    utilisation = _finite(record["Capacity Utilisation %"], "Capacity Utilisation %")
    quality = _finite(record["Quality Continuity Score"], "Quality Continuity Score")
    otif = _finite(record["OTIF %"], "OTIF %")

    profile_coil = {
        "CR_COIL_COMMERCIAL": (5.0, 15.0),
        "GI_COIL_Z120": (5.0, 15.0),
        "PPGI_COIL_Z120": (4.0, 12.0),
    }
    if profile_id not in profile_coil:
        raise ValueError(f"Unsupported Steel profile '{profile_id}'.")
    coil_min = float(record["Coil Weight Min MT"])
    coil_max = float(record["Coil Weight Max MT"])
    if not math.isfinite(coil_min) or not math.isfinite(coil_max) or coil_min <= 0 or coil_max < coil_min:
        raise ValueError("Contradictory coil-weight risk evidence.")
    req_min, req_max = profile_coil[profile_id]
    coil_mismatch = 0.0 if coil_min <= req_min and coil_max >= req_max else 100.0

    coating_dependency = controlled["coating_line_dependency_pct"] if profile_id != "CR_COIL_COMMERCIAL" else 0.0
    paint_dependency = controlled["paint_line_dependency_pct"] if profile_id == "PPGI_COIL_Z120" else 0.0
    dimensions = {
        "steel_index_volatility": _threshold_risk(controlled["steel_index_volatility_pct"], 15, 30),
        "ore_or_scrap_exposure": _threshold_risk(controlled["ore_or_scrap_exposure_pct"], 35, 65),
        "energy_exposure": _threshold_risk(controlled["energy_exposure_pct"], 30, 60),
        "mill_allocation": _threshold_risk(mill, 70, 85),
        "import_dependency": _threshold_risk(imports, 25, 60),
        "fx_exposure": _threshold_risk(controlled["fx_exposure_pct"], 20, 50),
        "duty_exposure": _threshold_risk(controlled["duty_exposure_pct"], 10, 30),
        "grade_substitution_dependency": _threshold_risk(controlled["grade_substitution_dependency_pct"], 10, 40),
        "coating_line_dependency": _threshold_risk(coating_dependency, 20, 50),
        "paint_line_dependency": _threshold_risk(paint_dependency, 20, 50),
        "source_concentration": _threshold_risk(concentration, 40, 70),
        "capacity_utilisation": _threshold_risk(utilisation, 75, 90),
        "coil_weight_mismatch": coil_mismatch,
        "quality_continuity": _threshold_risk(100.0 - quality, 10, 25),
        "delivery_continuity": _threshold_risk(100.0 - otif, 8, 18),
    }
    score = round(sum(dimensions[key] * STEEL_RISK_WEIGHTS[key] for key in STEEL_RISK_WEIGHTS), 2)
    return {
        "steel_risk_score": score,
        "steel_risk_band": _risk_band(score),
        "steel_risk_dimensions": dimensions,
        "steel_risk_weights": dict(STEEL_RISK_WEIGHTS),
        "steel_risk_assumptions": controlled,
    }


def score_and_recommend_steel_suppliers(
    suppliers: pd.DataFrame,
    profile_id: str,
    annual_volume_kg: float,
    usd_inr_fx: float,
    display_mode: str = "USD",
    risk_assumptions: Mapping | None = None,
    substitution_status: str = "Not applicable",
    substitution_requested: bool = False,
) -> tuple[pd.DataFrame, dict]:
    """Normalize, gate eligibility, score eligible suppliers, and return governed recommendation."""
    eligibility = evaluate_steel_supplier_table(
        suppliers, profile_id, annual_volume_kg, substitution_status, substitution_requested, display_mode
    )
    rows = []
    for position, (_, supplier) in enumerate(suppliers.iterrows()):
        quote = normalize_steel_supplier_quotation(
            supplier["Quoted Unit Price"], supplier["Quotation Currency"], annual_volume_kg, usd_inr_fx, display_mode
        )
        generic = calculate_generic_supplier_risk(supplier)
        steel = calculate_steel_specific_risk(supplier, profile_id, risk_assumptions)
        row = supplier.to_dict()
        row.update(quote)
        row.update({k: v for k, v in generic.items() if k != "generic_risk_dimensions"})
        row["generic_risk_dimensions"] = generic["generic_risk_dimensions"]
        row.update({k: v for k, v in steel.items() if k not in {"steel_risk_dimensions", "steel_risk_weights", "steel_risk_assumptions"}})
        row["steel_risk_dimensions"] = steel["steel_risk_dimensions"]
        row["technical_eligible"] = bool(eligibility.iloc[position]["eligible"])
        row["eligibility_failure_reasons"] = eligibility.iloc[position]["failure_reasons"]
        rows.append(row)

    scored = pd.DataFrame(rows)
    eligible_mask = scored["technical_eligible"]
    scored["commercial_score"] = 0.0
    if eligible_mask.any():
        minimum = scored.loc[eligible_mask, "normalized_usd_per_kg"].min()
        scored.loc[eligible_mask, "commercial_score"] = minimum / scored.loc[eligible_mask, "normalized_usd_per_kg"] * 100.0
    scored["generic_risk_fitness_score"] = 100.0 - scored["generic_risk_score"]
    scored["steel_risk_fitness_score"] = 100.0 - scored["steel_risk_score"]
    scored["performance_score"] = ((scored["OTIF %"] + scored["Audit Score"] + scored["Quality Continuity Score"]) / 3.0)
    scored["governed_total_score"] = (
        scored["commercial_score"] * STEEL_SCORE_WEIGHTS["commercial"]
        + scored["generic_risk_fitness_score"] * STEEL_SCORE_WEIGHTS["generic_risk_fitness"]
        + scored["steel_risk_fitness_score"] * STEEL_SCORE_WEIGHTS["steel_risk_fitness"]
        + scored["performance_score"] * STEEL_SCORE_WEIGHTS["performance"]
    ).round(2)
    scored.loc[~eligible_mask, "governed_total_score"] = 0.0
    scored = scored.sort_values(
        ["technical_eligible", "governed_total_score", "normalized_usd_per_kg", "Supplier"],
        ascending=[False, False, True, True],
    ).reset_index(drop=True)
    scored["governed_rank"] = range(1, len(scored) + 1)

    eligible = scored[scored["technical_eligible"]]
    if eligible.empty:
        recommendation = {
            "winner": None,
            "winner_state": "No winner — no technically eligible supplier",
            "human_approval_required": True,
            "autonomous_award": False,
        }
    else:
        winner = eligible.iloc[0]
        recommendation = {
            "winner": winner["Supplier"],
            "winner_state": "Governed recommendation — pending human approval",
            "normalized_usd_per_kg": float(winner["normalized_usd_per_kg"]),
            "governed_total_score": float(winner["governed_total_score"]),
            "generic_risk_score": float(winner["generic_risk_score"]),
            "steel_risk_score": float(winner["steel_risk_score"]),
            "human_approval_required": True,
            "autonomous_award": False,
        }
    scored.attrs.update({
        "eligible_supplier_count": int(eligible_mask.sum()),
        "calculation_currency": "USD",
        "comparison_unit": "USD/kg",
        "display_mode": display_mode,
        "score_weights": dict(STEEL_SCORE_WEIGHTS),
        "decision_boundary": "Synthetic decision support; not autonomous supplier approval or award.",
    })
    return scored, recommendation
