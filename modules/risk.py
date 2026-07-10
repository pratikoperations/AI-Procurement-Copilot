"""Structured supplier risk engine."""

from modules.utils import extract_number, normalize_score


def get_payment_days(value):
    text = str(value).lower()
    if "advance" in text:
        return 0
    import re
    match = re.search(r"net\s*(\d+)|(\d+)\s*days", text)
    if match:
        return int(match.group(1) or match.group(2))
    return 30


def get_advance_percent(value):
    text = str(value).lower()
    if "advance" not in text:
        return 0.0
    import re
    match = re.search(r"(\d+)\s*%", text)
    return int(match.group(1)) / 100 if match else 1.0


def normalize_incoterm(value):
    text = str(value).upper()
    for term in ["DDP", "DAP", "CIF", "FOB", "EXW"]:
        if term in text:
            return term
    return "UNKNOWN"


def calculate_risk(row):
    """Calculate auditable supplier risk score and risk breakdown."""
    payment_days = get_payment_days(row.get("Payment Terms", "Net 30"))
    advance_percent = get_advance_percent(row.get("Payment Terms", "Net 30"))
    incoterm = normalize_incoterm(row.get("Incoterms", "DDP"))
    lead_days = extract_number(row.get("Lead Time Days", 30), 30)
    moq = extract_number(row.get("MOQ", 10000), 10000)
    otif = float(row.get("OTIF %", 90))
    ppm = float(row.get("Quality PPM", 1000))

    risk = {
        "payment_risk": 25 if advance_percent > 0 else 10 if payment_days < 30 else 0,
        "incoterm_risk": 25 if incoterm == "EXW" else 15 if incoterm == "FOB" else 7 if incoterm == "CIF" else 0,
        "lead_time_risk": 20 if lead_days > 45 else 10 if lead_days > 30 else 5 if lead_days > 21 else 0,
        "moq_risk": 15 if moq > 200000 else 10 if moq > 75000 else 8 if moq > 50000 else 0,
        "service_risk": 15 if otif < 85 else 8 if otif < 90 else 0,
        "quality_risk": 20 if ppm > 2000 else 10 if ppm > 1200 else 5 if ppm > 900 else 0,
    }

    total_penalty = sum(risk.values())
    score = round(normalize_score(100 - total_penalty), 1)

    if score >= 75:
        label = "Low Risk"
    elif score >= 50:
        label = "Medium Risk"
    else:
        label = "High Risk"

    return {"risk_score": score, "risk_category": label, **risk}
