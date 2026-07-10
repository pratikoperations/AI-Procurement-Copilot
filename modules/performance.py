"""Supplier performance module placeholder for Build 0.2."""


def placeholder_performance_score(otif, quality_ppm):
    """Basic performance score placeholder. Full model arrives in Build 0.3."""
    ppm_penalty = min(float(quality_ppm) / 50, 40)
    return max(min(float(otif) - ppm_penalty, 100), 0)
