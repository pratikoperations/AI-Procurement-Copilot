"""Category-specific raw-material supplier risk engine."""

from modules.risk import get_advance_percent, get_payment_days, normalize_incoterm
from modules.utils import extract_number, normalize_score


def calculate_raw_material_risk(row):
    """Score commodity, supply, import, FX, substitution, quality, and capacity risks."""
    volatility = float(row.get("Commodity Volatility %", 15))
    import_dependency = float(row.get("Import Dependency %", 50))
    concentration = float(row.get("Supplier Concentration %", 50))
    substitute = str(row.get("Substitute Available", "Yes")).strip().lower() in {"yes", "y", "true", "1"}
    capacity_buffer = float(row.get("Capacity Buffer %", 10))
    quality_ppm = float(row.get("Quality PPM", 1000))
    currency = str(row.get("Currency", "USD")).upper()
    lead_days = extract_number(row.get("Lead Time Days", 30), 30)
    payment_days = get_payment_days(row.get("Payment Terms", "Net 30"))
    advance = get_advance_percent(row.get("Payment Terms", "Net 30"))
    incoterm = normalize_incoterm(row.get("Incoterms", "DDP"))

    penalties = {
        "commodity_volatility_risk": 20 if volatility > 30 else 12 if volatility > 20 else 6 if volatility > 10 else 0,
        "import_dependency_risk": 20 if import_dependency > 80 else 12 if import_dependency > 50 else 5 if import_dependency > 25 else 0,
        "concentration_risk": 20 if concentration > 80 else 12 if concentration > 60 else 5 if concentration > 40 else 0,
        "substitution_risk": 15 if not substitute else 0,
        "capacity_risk": 15 if capacity_buffer < 5 else 8 if capacity_buffer < 10 else 3 if capacity_buffer < 20 else 0,
        "quality_risk": 15 if quality_ppm > 2000 else 8 if quality_ppm > 1200 else 3 if quality_ppm > 700 else 0,
        "fx_risk": 10 if currency not in {"INR", "LOCAL"} else 0,
        "logistics_risk": 12 if lead_days > 60 else 8 if lead_days > 40 else 3 if lead_days > 25 else 0,
        "commercial_risk": 12 if advance > 0 else 5 if payment_days < 30 else 0,
        "incoterm_risk": 10 if incoterm == "EXW" else 7 if incoterm == "FOB" else 3 if incoterm == "CIF" else 0,
    }
    score = round(normalize_score(100 - sum(penalties.values())), 1)
    label = "Low Risk" if score >= 75 else "Medium Risk" if score >= 50 else "High Risk"
    return {"risk_score": score, "risk_category": label, **penalties}
