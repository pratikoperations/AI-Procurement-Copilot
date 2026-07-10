"""Supplier performance scoring engine."""

from modules.utils import normalize_score


def calculate_performance_score(row):
    """Calculate supplier performance score using OTIF, quality, audit, complaints, and capacity."""
    otif = float(row.get("OTIF %", 90))
    ppm = float(row.get("Quality PPM", 1000))
    audit_score = float(row.get("Audit Score", 80))
    complaint_rate = float(row.get("Complaint Rate %", 2.0))
    capacity_buffer = float(row.get("Capacity Buffer %", 10))

    ppm_score = max(100 - (ppm / 30), 0)
    complaint_score = max(100 - complaint_rate * 12, 0)
    capacity_score = min(capacity_buffer * 4, 100)

    score = (
        otif * 0.32
        + ppm_score * 0.23
        + audit_score * 0.23
        + complaint_score * 0.12
        + capacity_score * 0.10
    )
    return round(normalize_score(score), 1)
