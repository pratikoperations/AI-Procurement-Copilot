"""ESG and sustainability scoring engine."""

from modules.utils import normalize_score


def calculate_esg_score(row):
    """Calculate supplier ESG score using packaging-relevant sustainability signals."""
    recyclability = float(row.get("Recyclability", row.get("Recyclability %", 75)))
    certification = float(row.get("Certification", row.get("Certification Score", 75)))
    carbon_score = float(row.get("Carbon Score", 70))
    epr_readiness = float(row.get("EPR Readiness", 70))
    pcr_content = float(row.get("PCR Content %", 0))

    pcr_score = min(pcr_content * 2, 100)

    score = (
        recyclability * 0.30
        + certification * 0.25
        + carbon_score * 0.20
        + epr_readiness * 0.20
        + pcr_score * 0.05
    )
    return round(normalize_score(score), 1)
