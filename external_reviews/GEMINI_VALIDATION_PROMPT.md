# Gemini Independent Validation Prompt

Act as four reviewers simultaneously:

1. Senior procurement transformation leader
2. Packaging and raw-material category expert
3. Model-risk and governance reviewer
4. Software QA and adversarial-testing lead

Review the supplied repository code, architecture, formula register, assumption register, decision rules, expected-result matrix, validation datasets, screenshots and sample outputs.

## Required audit

Identify:

- Formula errors
- Unit or currency errors
- Double counting of cost or risk
- Unrealistic assumptions
- Misleading terminology
- Missing data-quality controls
- Incorrect packaging or raw-material category logic
- Unsafe recommendation behavior
- Infeasible allocation logic
- Weak negotiation logic
- Supplier 360 overstatement
- Financial-health overstatement
- ESG and innovation evidence gaps
- Contradictory classifications
- Cases where the system should refuse to recommend
- Cases where output confidence is overstated
- Missing regression tests

## Severity

Classify every finding as:

- Critical
- Major
- Moderate
- Minor
- Enhancement

## Required output format

For every finding provide:

- Finding ID
- Severity
- Module/file
- Description
- Procurement consequence
- Reproduction scenario
- Expected behavior
- Recommended correction
- Whether it blocks Portfolio Edition v1.0
- Confidence in finding

Do not suggest changes unless you explain the procurement rationale and expected consequence. Challenge the system rather than validating it by default.
