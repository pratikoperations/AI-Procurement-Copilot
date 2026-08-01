"""Metadata-only registry for scoring contributions, blockers and recommendation rules."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class GovernanceRule:
    rule_id: str
    version: str
    name: str
    rule_type: str
    category_applicability: Tuple[str, ...]
    source_file: str
    source_function: str
    deterministic_rule: str
    recommendation_impact: str
    blocking: bool
    human_approval_required: bool = True
    governance_notes: str = "Metadata only; authoritative rule execution remains in the cited service."


RULES = (
    GovernanceRule("RULE-WEIGHT-001", "1.0", "Weighted contribution", "weighted_contribution", ("Packaging", "Raw materials"), "modules/scoring.py", "enrich_supplier_scores", "factor score multiplied by governed profile weight", "changes ranking contribution", False),
    GovernanceRule("RULE-TECH-001", "1.0", "Technical ineligibility", "technical_ineligibility", ("All",), "umbrella: modules/kraft_paper_validation.py; modules/flexible_laminate_validation.py; modules/steel_validation.py; modules/scoring.py", "umbrella: validate_kraft_paper_dataframe; validate_flexible_laminate_dataframe; validate_steel_supplier_data; enrich_supplier_scores", "mandatory technical non-compliance remains ineligible", "removes supplier from eligible recommendation/allocation path", True),
    GovernanceRule("RULE-VAL-001", "1.0", "RFQ validation blocker", "validation_blocker", ("All",), "modules/recommendation_eligibility.py", "evaluate_recommendation_eligibility", "invalid RFQ prevents defensible recommendation", "status Blocked", True),
    GovernanceRule("RULE-BUS-001", "1.0", "Business-rule blocker", "business_rule_blocker", ("All",), "modules/recommendation_eligibility.py", "evaluate_recommendation_eligibility", "blocking issues prevent recommendation", "status Blocked", True),
    GovernanceRule("RULE-THR-001", "1.0", "Risk threshold failure", "threshold_failure", ("All",), "modules/recommendation_eligibility.py", "evaluate_recommendation_eligibility", "no supplier meets minimum risk threshold", "status Blocked or documented allocation fallback", True),
    GovernanceRule("RULE-WITHHOLD-001", "1.0", "Recommendation withholding", "recommendation_withholding", ("All",), "modules/recommendation_eligibility.py", "evaluate_recommendation_eligibility", "insufficient evidence limits permitted language", "withholds final award language", True),
    GovernanceRule("RULE-CONF-001", "1.0", "Confidence condition", "confidence_condition", ("All",), "modules/recommendation_eligibility.py", "evaluate_recommendation_eligibility", "confidence below 50/70/85 changes governed status", "Insufficient Data, Human Review Required or Eligible With Conditions", False),
    GovernanceRule("RULE-HUMAN-001", "1.0", "Mandatory human approval", "human_approval", ("All",), "modules/recommendation_eligibility.py", "evaluate_recommendation_eligibility", "human approval required for every award and allocation", "prevents autonomous decision claim", True),
)

DEFERRED_RULES = {
    "approved_deviation": "deferred — no exact authoritative approval service identified"
}
VALID_RULE_TYPES = {r.rule_type for r in RULES}
