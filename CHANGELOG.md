# Changelog

All meaningful project changes are recorded here.

## Build 0.9.2 — Intelligent RFQ Engine

### Added

- Flexible RFQ header recognition using exact and fuzzy matching.
- Canonical column mapping for supplier, price, MOQ, lead time, payment, incoterms, service, quality, ESG, currency, unit, material, and plant fields.
- Unit normalization for kg, MT, piece, meter, and liter.
- Duplicate supplier detection.
- Missing-cell and numeric-conversion diagnostics.
- Unmapped-column preservation.
- RFQ upload quality score and review warnings.
- Intelligent normalization integrated into CSV/Excel loading.
- Regression tests and RFQ-engine documentation.

### QA Notes

- Missing required fields block scoring after mapping.
- Unknown columns are preserved rather than discarded.
- CI and live alternate-template upload validation are pending.

## Build 0.9.1 — Multi-Category Foundation

- Added category routing, packaging/raw-material engine profiles, commodity metadata, selectors, guardrails, tests, and documentation.

## Build 0.8.1 — Deployment Stabilization

- Pinned Python 3.11 and exact dependencies and stabilized Streamlit deployment.

## Builds 0.1–0.8

Completed repository foundation, packaging intelligence, decision support, executive outputs, QA, CI, exports, portfolio assets, and public deployment.
