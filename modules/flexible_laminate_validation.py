"""Fail-closed validation for Flexible Laminates supplier data."""

from __future__ import annotations

import math
import pandas as pd

from modules.flexible_laminate_cost import ADHESIVE_TYPES, PRINT_PROCESSES, PRINT_PROFILES, SUPPORTED_STRUCTURES, TOOLING_AVAILABILITY

RISK_SCORE_COLUMNS = [
    "Substrate Availability %",
    "Press Capacity Utilisation %",
    "Lamination Capacity Utilisation %",
    "Printing Capability Score",
    "Lamination Capability Score",
    "Bond Strength Continuity Score",
    "Seal Integrity Continuity Score",
    "Solvent Retention Control Score",
]

REQUIRED_COLUMNS = [
    "Material", "Laminate Structure", "Layer Count", "Total Micron", "Unit",
    "Print Profile", "Print Process", "Number of Colours", "Adhesive Type",
    "Printing Loss %", "Lamination Loss %", "Slitting Loss %", "Tooling Status",
    "Existing Tooling Available", "Tooling Availability", "Tooling Cost per Colour USD",
    "Tooling Lifetime Volume kg", "Application Approval Status",
    *RISK_SCORE_COLUMNS,
]


def _numeric(series: pd.Series, column: str, errors: list[str]) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce")
    if values.isna().any():
        errors.append(f"'{column}' must contain a valid number in every Flexible Laminates row.")
    if values.map(lambda value: pd.notna(value) and not math.isfinite(float(value))).any():
        errors.append(f"'{column}' must contain finite values only.")
    return values


def validate_flexible_laminate_dataframe(df: pd.DataFrame, selected_structure: str | None) -> dict:
    """Return structured validation against one explicit laminate structure."""
    errors: list[str] = []
    warnings: list[str] = []
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        errors.append("Missing required Flexible Laminates fields: " + ", ".join(missing) + ".")
        return {"is_valid": False, "errors": errors, "warnings": warnings}

    if selected_structure is None:
        errors.append("Flexible Laminates validation requires an explicit selected structure.")
    elif selected_structure not in SUPPORTED_STRUCTURES:
        errors.append(f"Selected Flexible Laminates structure '{selected_structure}' is unsupported.")

    material = df["Material"].astype(str).str.strip()
    if material.eq("").any() or material.ne("Flexible Laminates").any():
        errors.append("Every Material value must be exactly 'Flexible Laminates'; blank or mixed materials are blocked.")

    structure = df["Laminate Structure"].astype(str).str.strip()
    invalid_structures = sorted(set(structure) - set(SUPPORTED_STRUCTURES))
    if invalid_structures:
        errors.append("Unsupported Flexible Laminates structure(s): " + ", ".join(invalid_structures) + ".")
    if selected_structure in SUPPORTED_STRUCTURES and structure.ne(selected_structure).any():
        errors.append(f"Every supplier quotation must match the selected laminate structure '{selected_structure}'; mixed or mismatched structures are blocked.")

    units = df["Unit"].astype(str).str.strip().str.lower()
    if units.ne("kg").any() or units.nunique() != 1:
        errors.append("Flexible Laminates supplier comparison requires kg-only quotations; mixed or non-kg units are blocked.")

    numeric_columns = [
        "Layer Count", "Total Micron", "Number of Colours", "Printing Loss %",
        "Lamination Loss %", "Slitting Loss %", "Tooling Cost per Colour USD",
        "Tooling Lifetime Volume kg", *RISK_SCORE_COLUMNS,
    ]
    numeric = {column: _numeric(df[column], column, errors) for column in numeric_columns}

    layer_count = numeric["Layer Count"]
    micron = numeric["Total Micron"]
    colours = numeric["Number of Colours"]
    print_loss = numeric["Printing Loss %"]
    lamination_loss = numeric["Lamination Loss %"]
    slitting_loss = numeric["Slitting Loss %"]
    tooling_cost = numeric["Tooling Cost per Colour USD"]
    tooling_volume = numeric["Tooling Lifetime Volume kg"]

    if not layer_count.isna().any() and (layer_count % 1 != 0).any(): errors.append("Layer Count must be a whole number.")
    if not micron.isna().any() and ((micron < 35) | (micron > 140)).any(): errors.append("Total Micron must be between 35 and 140 for the controlled C2 profiles.")
    if not colours.isna().any() and ((colours < 0) | (colours > 8) | (colours % 1 != 0)).any(): errors.append("Number of Colours must be a whole number between 0 and 8.")
    if not print_loss.isna().any() and ((print_loss < 0) | (print_loss > 8)).any(): errors.append("Printing Loss % must be between 0 and 8.")
    if not lamination_loss.isna().any() and ((lamination_loss < 0) | (lamination_loss > 6)).any(): errors.append("Lamination Loss % must be between 0 and 6.")
    if not slitting_loss.isna().any() and ((slitting_loss < 0) | (slitting_loss > 5)).any(): errors.append("Slitting Loss % must be between 0 and 5.")
    if not tooling_cost.isna().any() and (tooling_cost < 0).any(): errors.append("Tooling Cost per Colour USD must be non-negative.")

    for column in RISK_SCORE_COLUMNS:
        values = numeric[column]
        if not values.isna().any() and ((values < 0) | (values > 100)).any():
            errors.append(f"'{column}' must be between 0 and 100.")

    for index, row in df.iterrows():
        row_structure = str(row["Laminate Structure"]).strip()
        if row_structure in SUPPORTED_STRUCTURES and not pd.isna(layer_count.loc[index]) and float(layer_count.loc[index]).is_integer():
            expected = SUPPORTED_STRUCTURES[row_structure]["layer_count"]
            if int(layer_count.loc[index]) != expected:
                errors.append(f"{row.get('Supplier', 'Supplier')} has a layer-count mismatch for {row_structure}; expected {expected}.")

        print_profile = str(row["Print Profile"]).strip()
        print_process = str(row["Print Process"]).strip()
        adhesive_type = str(row["Adhesive Type"]).strip()
        tooling_status = str(row["Tooling Status"]).strip()
        existing_available = str(row["Existing Tooling Available"]).strip()
        tooling_available = str(row["Tooling Availability"]).strip()

        if print_profile not in PRINT_PROFILES: errors.append(f"Unsupported Print Profile '{print_profile}'.")
        if print_process not in PRINT_PROCESSES: errors.append(f"Unsupported Print Process '{print_process}'.")
        if adhesive_type not in ADHESIVE_TYPES: errors.append(f"Unsupported Adhesive Type '{adhesive_type}'.")
        if tooling_status not in {"New", "Existing", "Not applicable"}: errors.append(f"Unsupported Tooling Status '{tooling_status}'.")
        if existing_available not in TOOLING_AVAILABILITY: errors.append(f"Unsupported Existing Tooling Available value '{existing_available}'.")
        if tooling_available not in TOOLING_AVAILABILITY: errors.append(f"Unsupported Tooling Availability value '{tooling_available}'.")
        if tooling_available != existing_available:
            errors.append("Tooling Availability must match Existing Tooling Available for the controlled C2 contract.")

        if not pd.isna(colours.loc[index]) and float(colours.loc[index]).is_integer():
            count = int(colours.loc[index])
            valid_profile = (
                (print_profile == "Unprinted" and count == 0)
                or (print_profile == "Up to 4 colours" and 1 <= count <= 4)
                or (print_profile == "5–8 colours" and 5 <= count <= 8)
            )
            if print_profile in PRINT_PROFILES and not valid_profile:
                errors.append(f"Print Profile '{print_profile}' is inconsistent with {count} colours.")
            if print_profile == "Unprinted":
                if float(tooling_cost.loc[index]) != 0: errors.append("Unprinted Flexible Laminates rows must use zero tooling cost.")
                if tooling_status != "Not applicable" or tooling_available != "Not applicable": errors.append("Unprinted Flexible Laminates rows must use Not applicable tooling status and availability.")
            elif tooling_status == "New":
                if tooling_available != "Not applicable": errors.append("New tooling requires Tooling Availability to be Not applicable.")
                if float(tooling_volume.loc[index]) <= 0: errors.append("New print tooling requires a positive Tooling Lifetime Volume kg.")
            elif tooling_status == "Existing":
                if tooling_available not in {"Yes", "No", "Not assessed"}: errors.append("Existing tooling availability must be Yes, No, or Not assessed.")
                elif tooling_available != "Yes": errors.append("Existing tooling requires explicit Yes availability evidence before zero amortisation.")
            elif tooling_status == "Not applicable":
                errors.append("Printed Flexible Laminates rows must use New or Existing tooling status.")

    approval_values = set(df["Application Approval Status"].astype(str).str.strip())
    invalid_approvals = sorted(approval_values - {"Approved", "Conditional", "Not approved"})
    if invalid_approvals:
        errors.append("Unsupported Application Approval Status value(s): " + ", ".join(invalid_approvals) + ".")

    effective_loss = 1 - (1 - print_loss / 100) * (1 - lamination_loss / 100) * (1 - slitting_loss / 100)
    if not effective_loss.isna().any() and (effective_loss >= 0.15).any(): errors.append("Combined effective process loss must remain below 15%.")
    if not effective_loss.isna().any() and (effective_loss > 0.10).any(): warnings.append("One or more Flexible Laminates quotations have effective process loss above 10%; review yield assumptions.")

    return {"is_valid": not errors, "errors": list(dict.fromkeys(errors)), "warnings": list(dict.fromkeys(warnings))}
