"""Read-only scoring-weight metadata; existing scoring engines remain authoritative."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping, Tuple


@dataclass(frozen=True)
class WeightProfile:
    profile_id: str
    version: str
    name: str
    category_applicability: Tuple[str, ...]
    source_file: str
    source_function: str
    weights: Mapping[str, float]
    owner: str = "Procurement decision-support owner"
    status: str = "active"
    effective_date: str | None = None
    governance_notes: str = "Read-only metadata; changes require separate governance approval."


WEIGHT_PROFILES = (
    WeightProfile("WGT-PKG-001", "1.0", "Generic Packaging", ("Packaging Procurement",), "modules/scoring.py", "enrich_supplier_scores", {"tco": .40, "risk": .20, "lead_time": .10, "payment": .08, "moq": .07, "performance": .10, "esg": .05}),
    WeightProfile("WGT-RM-001", "1.0", "Generic Raw Materials", ("Raw Material Procurement",), "modules/scoring.py", "enrich_supplier_scores", {"tco": .38, "risk": .27, "lead_time": .08, "payment": .07, "moq": .05, "performance": .10, "esg": .05}),
    WeightProfile("WGT-STL-001", "1.0", "Governed Steel", ("Steel",), "modules/steel_risk.py", "score_and_recommend_steel_suppliers", {}, governance_notes="Dedicated governed Steel scoring; no generic weight substitution is permitted."),
)


def profile_by_id(profile_id: str) -> WeightProfile:
    return next(item for item in WEIGHT_PROFILES if item.profile_id == profile_id)


def validate_weight_profiles() -> None:
    for profile in WEIGHT_PROFILES:
        if profile.weights and abs(sum(profile.weights.values()) - 1.0) > 1e-9:
            raise ValueError(f"Weight profile {profile.profile_id} does not sum to 1.0")
