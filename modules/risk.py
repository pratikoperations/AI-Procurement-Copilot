"""Supplier risk module placeholder for Build 0.2."""


def placeholder_risk_score(risk_category):
    """Map basic risk category to score. Full risk engine arrives in Build 0.3."""
    mapping = {
        "Low": 85,
        "Medium": 65,
        "High": 40,
    }
    return mapping.get(str(risk_category).title(), 60)
