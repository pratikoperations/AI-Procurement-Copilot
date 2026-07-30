"""Controlled Kraft Paper technical and sourcing validation."""

SUPPORTED_VARIANTS = {"Recycled Kraft", "Virgin Kraft"}
SUPPORTED_GSM = {120, 150, 180}
SUPPORTED_STRENGTH = {"18 BF", "22 BF", "28 BF"}


def validate_kraft_paper_dataframe(df):
    """Return blocking errors and review warnings for Kraft Paper supplier data."""
    errors, warnings = [], []
    required = [
        "Kraft Variant", "GSM", "Strength Grade", "Mill Allocation %", "Moisture %",
        "Recycled Fibre Availability %", "Quality Continuity Score", "Corrugated Linkage",
    ]
    missing = [column for column in required if column not in df.columns]
    if missing:
        errors.append("Missing Kraft Paper fields: " + ", ".join(missing))
        return {"is_valid": False, "errors": errors, "warnings": warnings}

    invalid_variants = sorted(set(df["Kraft Variant"].dropna()) - SUPPORTED_VARIANTS)
    if invalid_variants:
        errors.append("Unsupported Kraft Paper variants: " + ", ".join(map(str, invalid_variants)))
    invalid_gsm = sorted(set(df["GSM"].dropna().astype(int)) - SUPPORTED_GSM)
    if invalid_gsm:
        errors.append("Unsupported Kraft Paper GSM values: " + ", ".join(map(str, invalid_gsm)))
    invalid_strength = sorted(set(df["Strength Grade"].dropna()) - SUPPORTED_STRENGTH)
    if invalid_strength:
        errors.append("Unsupported Kraft Paper strength grades: " + ", ".join(map(str, invalid_strength)))
    if not df["Unit"].astype(str).str.lower().eq("kg").all():
        errors.append("Kraft Paper quotations must use kg as the comparison unit.")
    if (df["Moisture %"] <= 0).any() or (df["Moisture %"] > 15).any():
        errors.append("Kraft Paper moisture must be greater than 0% and no more than 15%.")
    if (df["Mill Allocation %"] > 85).any():
        warnings.append("One or more suppliers exceed 85% mill allocation; continuity review is required.")
    if (df["Moisture %"] > 9).any():
        warnings.append("One or more suppliers exceed 9% moisture; quality and yield review is required.")
    if (df["Recycled Fibre Availability %"] < 65).any():
        warnings.append("Low recycled-fibre availability may constrain supply or increase paper-price exposure.")
    if (df["Quality Continuity Score"] < 70).any():
        warnings.append("One or more suppliers have a quality-continuity score below 70/100.")
    if df["Corrugated Linkage"].astype(str).str.strip().eq("").any():
        errors.append("Every Kraft Paper profile requires a controlled Corrugated Board linkage statement.")
    return {"is_valid": not errors, "errors": errors, "warnings": warnings}
