# Business Rules

## Governance Status

This document records the stable v1.0.0 rule contract. Executable code and regression tests remain authoritative where implementation detail is required. Any formula, weight, threshold, or eligibility change requires explicit approval, tests, and changelog entry.

## Stable Integrity Rules

1. Preserve Original Currency and Original Unit Price.
2. Keep Normalized Currency, Normalized Unit Price, FX Rate Used, Unit of Measure, and Comparison Basis explicit.
3. Block unsupported currency conversion rather than inventing an exchange rate.
4. Use category-appropriate units; PET Resin standard demo uses kg.
5. Do not store non-USD values in USD-labelled comparison fields.
6. Use the visible term `Risk Resilience Score`.
7. Distinguish RFQ performance scores from governed Supplier 360 scores.
8. Freight stress must affect unit and annual TCO in Packaging and Raw Material scenarios.
9. Scenario outputs must support governed and documented legacy schema labels.
10. Final-award language must be withheld when eligibility or evidence is insufficient.
11. Weak evidence must cap Financial, ESG, Innovation, and long-term supplier conclusions.
12. Exit Candidate and Development Candidate cannot be assigned simultaneously to one supplier.
13. Readable executive exports and technical audit outputs must remain separated.
14. Supplier communication must reflect category, validation status, and evidence gaps.
15. Human procurement approval and due diligence are mandatory.

## Missing-Data Behaviour

- Missing mandatory fields: block or mark the relevant workflow ineligible.
- Missing optional evidence: retain the supplier where possible, lower confidence, cap conclusions, and disclose the gap.
- Unsupported unit or currency: do not silently normalize.
- Missing validation evidence: use provisional language and require human review.
- Demo data: clearly identify it as synthetic and unsuitable for real award execution.

## Formula Governance

Current formulas, weights, and thresholds must be read from the relevant implementation modules and verified by tests before modification. Do not copy a value from chat history into code without confirming the current repository implementation.

For every formula change, document:

- Previous and proposed formula
- Business rationale
- Units and currency basis
- Boundary and missing-data behaviour
- Suppliers/categories affected
- Test cases and expected results
- Approval owner

## Decision Boundary

Outputs are recommendations and decision-support evidence. The application does not autonomously approve suppliers, execute awards, replace due diligence, or substitute for commercial, legal, quality, financial, compliance, sustainability, treasury, tax, or executive review.
