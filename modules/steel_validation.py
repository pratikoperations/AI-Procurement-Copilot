"""Fail-closed technical eligibility for governed C3 Steel profiles."""

from __future__ import annotations

import math
from typing import Mapping

import pandas as pd


STEEL_PROFILES = {
    "CR_COIL_COMMERCIAL": {
        "grade_token": "CR commercial demonstration",
        "thickness_mm": 0.80,
        "width_min_mm": 1000.0,
        "width_max_mm": 1250.0,
        "zinc_gsm": 0.0,
        "requires_paint_line": False,
        "surface_token": "commercial",
        "coil_min_mt": 5.0,
        "coil_max_mt": 15.0,
    },
    "GI_COIL_Z120": {
        "grade_token": "GI substrate demonstration",
        "thickness_mm": 0.60,
        "width_min_mm": 1000.0,
        "width_max_mm": 1250.0,
        "zinc_gsm": 120.0,
        "requires_paint_line": False,
        "surface_token": "galvanized",
        "coil_min_mt": 5.0,
        "coil_max_mt": 15.0,
    },
    "PPGI_COIL_Z120": {
        "grade_token": "PPGI substrate demonstration",
        "thickness_mm": 0.50,
        "width_min_mm": 1000.0,
        "width_max_mm": 1250.0,
        "zinc_gsm": 120.0,
        "requires_paint_line": True,
        "surface_token": "pre-painted",
        "coil_min_mt": 4.0,
        "coil_max_mt": 12.0,
    },
}

DISPLAY_MODES = {"USD", "INR", "Both"}
REQUIRED_FIELDS = (
    "Supplier",
    "Supported Steel Profiles",
    "Controlled Grade Families",
    "Thickness Min mm",
    "Thickness Max mm",
    "Width Min mm",
    "Width Max mm",
    "Zinc Capability Max g/m²",
    "Paint Line Capability",
    "Surface Capability",
    "Supplier or Mill Approval",
    "Application Approval",
    "Test Certificate Availability",
    "Supplier Capacity",
    "Capacity Utilisation %",
    "Coil Weight Min MT",
    "Coil Weight Max MT",
)


def _missing(value) -> bool:
    if value is None:
        return True
    try:
        if pd.isna(value):
            return True
    except (TypeError, ValueError):
        pass
    return isinstance(value, str) and not value.strip()


def _number(value, label: str) -> float:
    if _missing(value) or isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a finite numeric value.")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{label} must be a finite numeric value.")
    return number


def _tokens(value) -> set[str]:
    if _missing(value):
        return set()
    return {part.strip().casefold() for part in str(value).split("|") if part.strip()}


def _approved(value) -> bool:
    return not _missing(value) and str(value).strip().casefold() == "approved"


def _certificate_available(value) -> bool:
    if _missing(value):
        return False
    state = str(value).strip().casefold()
    return state.startswith("available") and not any(word in state for word in ("unavailable", "pending"))


def _substitution_valid(status: str, substitution_requested: bool) -> bool:
    if _missing(status):
        return False
    normalized = str(status).strip().casefold()
    if substitution_requested:
        return normalized == "approved"
    return normalized in {"not applicable", "approved"}


def evaluate_steel_supplier_eligibility(
    supplier: Mapping,
    profile_id: str,
    annual_volume_kg: float,
    substitution_status: str = "Not applicable",
    substitution_requested: bool = False,
    display_mode: str = "USD",
) -> dict:
    """Evaluate one supplier against the controlled Steel specification.

    Eligibility is independent of quotation price, risk category and display currency.
    All mandatory failures are returned to support deterministic governance evidence.
    """
    if profile_id not in STEEL_PROFILES:
        raise ValueError(f"Unsupported Steel profile '{profile_id}'.")
    if display_mode not in DISPLAY_MODES:
        raise ValueError(f"Unsupported Steel display mode '{display_mode}'.")
    volume = _number(annual_volume_kg, "Annual volume")
    if volume <= 0:
        raise ValueError("Annual volume must be greater than zero.")

    profile = STEEL_PROFILES[profile_id]
    failures: list[str] = []

    for field in REQUIRED_FIELDS:
        if field not in supplier or _missing(supplier.get(field)):
            failures.append(f"Missing mandatory field: {field}")

    supported_profiles = _tokens(supplier.get("Supported Steel Profiles"))
    if profile_id.casefold() not in supported_profiles:
        failures.append("Selected profile is not explicitly supported")

    grade_families = _tokens(supplier.get("Controlled Grade Families"))
    if profile["grade_token"].casefold() not in grade_families:
        failures.append("Controlled grade family is not supported")

    numeric = {}
    numeric_fields = (
        "Thickness Min mm", "Thickness Max mm", "Width Min mm", "Width Max mm",
        "Zinc Capability Max g/m²", "Supplier Capacity", "Capacity Utilisation %",
        "Coil Weight Min MT", "Coil Weight Max MT",
    )
    for field in numeric_fields:
        try:
            numeric[field] = _number(supplier.get(field), field)
        except ValueError:
            failures.append(f"Invalid mandatory numeric field: {field}")

    if {"Thickness Min mm", "Thickness Max mm"} <= numeric.keys():
        low, high = numeric["Thickness Min mm"], numeric["Thickness Max mm"]
        if low < 0 or high < low:
            failures.append("Contradictory thickness capability range")
        elif not low <= profile["thickness_mm"] <= high:
            failures.append("Required thickness is outside supplier capability")

    if {"Width Min mm", "Width Max mm"} <= numeric.keys():
        low, high = numeric["Width Min mm"], numeric["Width Max mm"]
        if low < 0 or high < low:
            failures.append("Contradictory width capability range")
        elif low > profile["width_min_mm"] or high < profile["width_max_mm"]:
            failures.append("Required width band is not fully supported")

    if "Zinc Capability Max g/m²" in numeric:
        zinc = numeric["Zinc Capability Max g/m²"]
        if zinc < 0:
            failures.append("Zinc capability cannot be negative")
        elif zinc < profile["zinc_gsm"]:
            failures.append("Required zinc coating exceeds supplier capability")

    paint_state = supplier.get("Paint Line Capability")
    if not _missing(paint_state):
        normalized_paint = str(paint_state).strip().casefold()
        if normalized_paint not in {"yes", "no"}:
            failures.append("Paint-line capability is contradictory or unsupported")
        elif profile["requires_paint_line"] and normalized_paint != "yes":
            failures.append("Selected profile requires paint-line capability")

    surfaces = _tokens(supplier.get("Surface Capability"))
    if not any(profile["surface_token"] in token for token in surfaces):
        failures.append("Required surface capability is not supported")

    if not _approved(supplier.get("Supplier or Mill Approval")):
        failures.append("Supplier or mill approval is not Approved")
    if not _approved(supplier.get("Application Approval")):
        failures.append("Application approval is not Approved")
    if not _certificate_available(supplier.get("Test Certificate Availability")):
        failures.append("Test certificate is not available")

    if "Supplier Capacity" in numeric:
        capacity = numeric["Supplier Capacity"]
        if capacity <= 0:
            failures.append("Supplier capacity must be positive")
        elif volume > capacity:
            failures.append("Annual volume exceeds supplier capacity")
    if "Capacity Utilisation %" in numeric:
        utilisation = numeric["Capacity Utilisation %"]
        if not 0 <= utilisation < 100:
            failures.append("Capacity utilisation must be within 0% to below 100%")

    if {"Coil Weight Min MT", "Coil Weight Max MT"} <= numeric.keys():
        low, high = numeric["Coil Weight Min MT"], numeric["Coil Weight Max MT"]
        if low <= 0 or high < low:
            failures.append("Contradictory coil-weight capability range")
        elif low > profile["coil_min_mt"] or high < profile["coil_max_mt"]:
            failures.append("Required coil-weight band is not fully supported")

    if not _substitution_valid(substitution_status, substitution_requested):
        failures.append("Substitution approval state is not valid for the request")

    return {
        "supplier": supplier.get("Supplier"),
        "profile_id": profile_id,
        "eligible": not failures,
        "eligibility_status": "Eligible" if not failures else "Ineligible",
        "failure_reasons": failures,
        "failure_count": len(failures),
        "display_mode": display_mode,
        "annual_volume_kg": volume,
        "substitution_requested": bool(substitution_requested),
        "substitution_status": substitution_status,
        "decision_basis": "Technical eligibility only; price and risk cannot override failures.",
    }


def evaluate_steel_supplier_table(
    suppliers: pd.DataFrame,
    profile_id: str,
    annual_volume_kg: float,
    substitution_status: str = "Not applicable",
    substitution_requested: bool = False,
    display_mode: str = "USD",
) -> pd.DataFrame:
    """Return deterministic eligibility evidence for every supplier row."""
    if not isinstance(suppliers, pd.DataFrame):
        raise ValueError("Steel suppliers must be provided as a pandas DataFrame.")
    results = [
        evaluate_steel_supplier_eligibility(
            row,
            profile_id,
            annual_volume_kg,
            substitution_status,
            substitution_requested,
            display_mode,
        )
        for _, row in suppliers.iterrows()
    ]
    frame = pd.DataFrame(results)
    frame.attrs["eligible_supplier_count"] = int(frame["eligible"].sum()) if not frame.empty else 0
    frame.attrs["eligibility_state"] = "Eligible suppliers available" if frame.attrs["eligible_supplier_count"] else "No eligible suppliers"
    return frame


def steel_eligibility_summary(results: pd.DataFrame) -> dict:
    """Return explicit eligible-count and no-winner state for later phases."""
    if not isinstance(results, pd.DataFrame) or "eligible" not in results.columns:
        raise ValueError("Steel eligibility results must contain an eligible column.")
    count = int(results["eligible"].sum())
    return {
        "eligible_supplier_count": count,
        "eligibility_state": "Eligible suppliers available" if count else "No eligible suppliers",
        "winner_state": "Not evaluated — C3.4 authorization required" if count else "No winner — no technically eligible supplier",
    }


def lowest_price_eligible_supplier(
    suppliers: pd.DataFrame,
    results: pd.DataFrame,
    normalized_price_column: str = "Normalized USD/kg",
) -> dict:
    """Demonstrate that only eligible suppliers can enter later winner selection."""
    if normalized_price_column not in suppliers.columns:
        raise ValueError(f"Missing normalized price column '{normalized_price_column}'.")
    if len(suppliers) != len(results):
        raise ValueError("Supplier and eligibility rows must reconcile one-to-one.")
    eligible_positions = [position for position, value in enumerate(results["eligible"].tolist()) if bool(value)]
    if not eligible_positions:
        return {"winner_state": "No winner — no technically eligible supplier", "supplier": None}
    candidates = suppliers.iloc[eligible_positions].copy()
    prices = pd.to_numeric(candidates[normalized_price_column], errors="coerce")
    if prices.isna().any() or not prices.map(math.isfinite).all():
        raise ValueError("Eligible supplier normalized prices must be finite numeric values.")
    winning_position = prices.idxmin()
    return {
        "winner_state": "Provisional eligible-only price result; C3.4 recommendation not implemented",
        "supplier": suppliers.loc[winning_position, "Supplier"],
        "normalized_usd_per_kg": float(suppliers.loc[winning_position, normalized_price_column]),
    }
