"""Controlled Kraft Paper technical and sourcing validation."""

from __future__ import annotations

import pandas as pd

SUPPORTED_VARIANTS = {"Recycled Kraft", "Virgin Kraft"}
SUPPORTED_GSM = {120, 150, 180}
SUPPORTED_STRENGTH = {"18 BF", "22 BF", "28 BF"}
SUPPORTED_CORRUGATED_LINKAGES = {
    "Approved demonstration assumption",
    "Conditional demonstration assumption",
}

REQUIRED_KRAFT_COLUMNS = [
    "Material",
    "Kraft Variant",
    "GSM",
    "Strength Grade",
    "Unit",
    "Mill Allocation %",
    "Moisture %",
    "Fibre Availability %",
    "Quality Continuity Score",
    "Corrugated Linkage",
]


def _numeric_series(df, column, errors):
    """Return a numeric series while recording governed validation errors."""
    values = pd.to_numeric(df[column], errors="coerce")
    if values.isna().any():
        errors.append(f"Kraft Paper field '{column}' contains blank or non-numeric values.")
    return values


def validate_kraft_paper_dataframe(df):
    """Return blocking errors and review warnings for Kraft Paper supplier data."""
    errors, warnings = [], []
    missing = [column for column in REQUIRED_KRAFT_COLUMNS if column not in df.columns]
    if missing:
        errors.append("Missing Kraft Paper fields: " + ", ".join(missing))
        return {"is_valid": False, "errors": errors, "warnings": warnings}

    material = df["Material"].astype(str).str.strip()
    if material.eq("").any() or not material.eq("Kraft Paper").all():
        errors.append("Kraft Paper analysis requires every Material value to equal 'Kraft Paper'. Mixed, blank, or conflicting materials are blocked.")

    variants = df["Kraft Variant"].astype(str).str.strip()
    if variants.eq("").any():
        errors.append("Kraft Paper variant cannot be blank.")
    invalid_variants = sorted(set(variants) - SUPPORTED_VARIANTS - {""})
    if invalid_variants:
        errors.append("Unsupported Kraft Paper variants: " + ", ".join(invalid_variants))

    gsm = _numeric_series(df, "GSM", errors)
    valid_gsm = gsm.dropna()
    if ((valid_gsm % 1) != 0).any():
        errors.append("Kraft Paper GSM must be a whole-number controlled profile.")
    invalid_gsm = sorted(set(valid_gsm.astype(int)) - SUPPORTED_GSM)
    if invalid_gsm:
        errors.append("Unsupported Kraft Paper GSM values: " + ", ".join(map(str, invalid_gsm)))

    strength = df["Strength Grade"].astype(str).str.strip()
    if strength.eq("").any():
        errors.append("Kraft Paper strength grade cannot be blank.")
    invalid_strength = sorted(set(strength) - SUPPORTED_STRENGTH - {""})
    if invalid_strength:
        errors.append("Unsupported Kraft Paper strength grades: " + ", ".join(invalid_strength))

    units = df["Unit"].astype(str).str.strip().str.lower()
    if units.eq("").any() or not units.eq("kg").all():
        errors.append("Kraft Paper quotations must use kg as the comparison unit.")

    mill_allocation = _numeric_series(df, "Mill Allocation %", errors)
    moisture = _numeric_series(df, "Moisture %", errors)
    fibre_availability = _numeric_series(df, "Fibre Availability %", errors)
    quality_continuity = _numeric_series(df, "Quality Continuity Score", errors)

    for column, values in {
        "Mill Allocation %": mill_allocation,
        "Fibre Availability %": fibre_availability,
        "Quality Continuity Score": quality_continuity,
    }.items():
        valid = values.dropna()
        if ((valid < 0) | (valid > 100)).any():
            errors.append(f"Kraft Paper field '{column}' must be between 0 and 100.")

    valid_moisture = moisture.dropna()
    if ((valid_moisture <= 0) | (valid_moisture > 15)).any():
        errors.append("Kraft Paper moisture must be greater than 0% and no more than 15%.")

    linkages = df["Corrugated Linkage"].astype(str).str.strip()
    invalid_linkages = sorted(set(linkages) - SUPPORTED_CORRUGATED_LINKAGES)
    if invalid_linkages:
        errors.append("Unsupported Corrugated Board linkage values: " + ", ".join(invalid_linkages))

    if (mill_allocation.dropna() > 85).any():
        warnings.append("One or more suppliers exceed 85% mill allocation; continuity review is required.")
    if (moisture.dropna() > 9).any():
        warnings.append("One or more suppliers exceed 9% moisture; quality and yield review is required.")
    if (fibre_availability.dropna() < 65).any():
        warnings.append("Low fibre availability may constrain supply or increase paper-price exposure.")
    if (quality_continuity.dropna() < 70).any():
        warnings.append("One or more suppliers have a quality-continuity score below 70/100.")

    return {
        "is_valid": not errors,
        "errors": list(dict.fromkeys(errors)),
        "warnings": list(dict.fromkeys(warnings)),
    }
