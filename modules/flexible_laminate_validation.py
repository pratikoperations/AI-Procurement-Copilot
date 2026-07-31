"""Fail-closed validation for Flexible Laminates supplier data."""

from __future__ import annotations

import pandas as pd

from modules.flexible_laminate_cost import (
    ADHESIVE_TYPES,
    PRINT_PROCESSES,
    PRINT_PROFILES,
    SUPPORTED_STRUCTURES,
)

REQUIRED_COLUMNS = [
    "Material",
    "Laminate Structure",
    "Layer Count",
    "Total Micron",
    "Unit",
    "Print Profile",
    "Print Process",
    "Number of Colours",
    "Adhesive Type",
    "Printing Loss %",
    "Lamination Loss %",
    "Slitting Loss %",
    "Tooling Status",
    "Tooling Cost per Colour USD",
    "Tooling Lifetime Volume kg",
    "Application Approval Status",
    "Printing Capability Score",
    "Lamination Capability Score",
]


def _numeric(series: pd.Series, column: str, errors: list[str]) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce")
    if values.isna().any():
        errors.append(f"'{column}' must contain a valid number in every Flexible Laminates row.")
    return values


def validate_flexible_laminate_dataframe(df: pd.DataFrame) -> dict:
    """Return structured Flexible Laminates validation results."""
    errors: list[str] = []
    warnings: list[str] = []
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        errors.append("Missing required Flexible Laminates fields: " + ", ".join(missing) + ".")
        return {"is_valid": False, "errors": errors, "warnings": warnings}

    material = df["Material"].astype(str).str.strip()
    if material.eq("").any() or material.ne("Flexible Laminates").any():
        errors.append("Every Material value must be exactly 'Flexible Laminates'; blank or mixed materials are blocked.")

    structure = df["Laminate Structure"].astype(str).str.strip()
    invalid_structures = sorted(set(structure) - set(SUPPORTED_STRUCTURES))
    if invalid_structures:
        errors.append("Unsupported Flexible Laminates structure(s): " + ", ".join(invalid_structures) + ".")

    units = df["Unit"].astype(str).str.strip().str.lower()
    if units.ne("kg").any() or units.nunique() != 1:
        errors.append("Flexible Laminates supplier comparison requires kg-only quotations; mixed or non-kg units are blocked.")

    layer_count = _numeric(df["Layer Count"], "Layer Count", errors)
    micron = _numeric(df["Total Micron"], "Total Micron", errors)
    colours = _numeric(df["Number of Colours"], "Number of Colours", errors)
    print_loss = _numeric(df["Printing Loss %"], "Printing Loss %", errors)
    lamination_loss = _numeric(df["Lamination Loss %"], "Lamination Loss %", errors)
    slitting_loss = _numeric(df["Slitting Loss %"], "Slitting Loss %", errors)
    tooling_cost = _numeric(df["Tooling Cost per Colour USD"], "Tooling Cost per Colour USD", errors)
    tooling_volume = _numeric(df["Tooling Lifetime Volume kg"], "Tooling Lifetime Volume kg", errors)

    if not micron.isna().any() and ((micron < 35) | (micron > 140)).any():
        errors.append("Total Micron must be between 35 and 140 for the controlled C2 profiles.")
    if not colours.isna().any() and ((colours < 0) | (colours > 8) | (colours % 1 != 0)).any():
        errors.append("Number of Colours must be a whole number between 0 and 8.")
    if not print_loss.isna().any() and ((print_loss < 0) | (print_loss > 8)).any():
        errors.append("Printing Loss % must be between 0 and 8.")
    if not lamination_loss.isna().any() and ((lamination_loss < 0) | (lamination_loss > 6)).any():
        errors.append("Lamination Loss % must be between 0 and 6.")
    if not slitting_loss.isna().any() and ((slitting_loss < 0) | (slitting_loss > 5)).any():
        errors.append("Slitting Loss % must be between 0 and 5.")
    if not tooling_cost.isna().any() and (tooling_cost < 0).any():
        errors.append("Tooling Cost per Colour USD must be non-negative.")

    for index, row in df.iterrows():
        row_structure = str(row["Laminate Structure"]).strip()
        if row_structure in SUPPORTED_STRUCTURES and not pd.isna(layer_count.loc[index]):
            expected = SUPPORTED_STRUCTURES[row_structure]["layer_count"]
            if int(layer_count.loc[index]) != expected:
                errors.append(f"{row.get('Supplier', 'Supplier')} has a layer-count mismatch for {row_structure}; expected {expected}.")
        print_profile = str(row["Print Profile"]).strip()
        print_process = str(row["Print Process"]).strip()
        adhesive_type = str(row["Adhesive Type"]).strip()
        tooling_status = str(row["Tooling Status"]).strip()
        if print_profile not in PRINT_PROFILES:
            errors.append(f"Unsupported Print Profile '{print_profile}'.")
        if print_process not in PRINT_PROCESSES:
            errors.append(f"Unsupported Print Process '{print_process}'.")
        if adhesive_type not in ADHESIVE_TYPES:
            errors.append(f"Unsupported Adhesive Type '{adhesive_type}'.")
        if tooling_status not in {"New", "Existing", "Not applicable"}:
            errors.append(f"Unsupported Tooling Status '{tooling_status}'.")
        if not pd.isna(colours.loc[index]):
            colour_count = int(colours.loc[index])
            if print_profile == "Unprinted" and (colour_count != 0 or float(tooling_cost.loc[index]) != 0):
                errors.append("Unprinted Flexible Laminates rows must use zero colours and zero tooling cost.")
            if print_profile != "Unprinted" and colour_count == 0:
                errors.append("Printed Flexible Laminates rows require at least one colour.")
            if print_profile != "Unprinted" and tooling_status == "New" and float(tooling_volume.loc[index]) <= 0:
                errors.append("New print tooling requires a positive Tooling Lifetime Volume kg.")

    controlled = {
        "Application Approval Status": {"Approved", "Conditional", "Not approved"},
    }
    for column, values in controlled.items():
        invalid = sorted(set(df[column].astype(str).str.strip()) - values)
        if invalid:
            errors.append(f"Unsupported {column} value(s): " + ", ".join(invalid) + ".")

    for column in ["Printing Capability Score", "Lamination Capability Score"]:
        numeric = _numeric(df[column], column, errors)
        if not numeric.isna().any() and ((numeric < 0) | (numeric > 100)).any():
            errors.append(f"'{column}' must be between 0 and 100.")

    effective_loss = 1 - (1 - print_loss / 100) * (1 - lamination_loss / 100) * (1 - slitting_loss / 100)
    if not effective_loss.isna().any() and (effective_loss >= 0.15).any():
        errors.append("Combined effective process loss must remain below 15%.")
    if not effective_loss.isna().any() and (effective_loss > 0.10).any():
        warnings.append("One or more Flexible Laminates quotations have effective process loss above 10%; review yield assumptions.")

    return {
        "is_valid": not errors,
        "errors": list(dict.fromkeys(errors)),
        "warnings": list(dict.fromkeys(warnings)),
    }
