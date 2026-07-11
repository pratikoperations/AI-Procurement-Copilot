# Changelog

All meaningful project changes are recorded here.

## Build 0.9.6 — Independent Validation and Real-World Stress Testing

### Added

- Data-confidence engine measuring supplied, defaulted, inferred and missing-critical data.
- Recommendation eligibility gate with Eligible, Eligible With Conditions, Human Review Required, Insufficient Data and Blocked states.
- Business-rule validator for price, volume, percentages, capacity, allocation, currency, UOM and contradictory statuses.
- Safe executive-output withholding when validation does not permit final award language.
- Formula, assumption, decision-rule and traceability registers.
- Known model limitations and model-risk statement.
- Adversarial, boundary, eligibility, data-confidence, rule and real-world file tests.
- Fourteen synthetic packaging, raw-material and edge-case validation files.
- Expected-result matrix and validation defect register.
- Gemini, Perplexity and human-review framework.
- Release-readiness scorecard and validation reports.

### Changed

- `app.py` now displays data confidence, eligibility and business-rule status before recommendation outputs.
- Blocked or insufficient-data cases no longer display polished final-award language.
- Demo data and uploaded unverified data are visibly distinguished.

### Validation Notes

- Internal implementation is complete.
- Latest CI, live Streamlit validation, Gemini review, Perplexity review and human review remain pending.
- Portfolio Edition v1.0 is not yet approved.

## Build 0.9.5 — Supplier Intelligence Platform

- Added Supplier 360, extended performance, financial indicators, ESG, innovation, SRM, recommendations, comparison, narrative, exports and tests.
- CI validated.

## Build 0.9.4 — Category-Specific Cost and Risk Engines

- Added production raw-material should-cost, risk, TCO, category-aware scoring and routing.
- CI validated.

## Builds 0.1–0.9.3.1

Completed repository foundation, packaging intelligence, executive outputs, CI, deployment stabilization, multi-category foundation, Intelligent RFQ, Procurement Intelligence and integration hotfixes.
