# Changelog

All meaningful project changes are recorded here.

## Build 0.9.3.1 — Category Profile Integration Hotfix

### Fixed

- Eliminated startup `KeyError: 'category_profile'`.
- Added a reusable default category profile.
- Guaranteed the sidebar return contract includes `category_profile`.
- Added defensive profile normalization in `app.py`.
- Added regression tests for normal, partial, and missing profile cases.
- Added hotfix documentation and governance updates.

### QA Notes

- No procurement logic was changed.
- Build 0.9.3 functionality is preserved.
- CI and live deployment validation are pending.

## Build 0.9.3 — Procurement Intelligence Engine

- Added executive decision, strategy, allocation, negotiation, risk, scenario, explainability, dashboard, tests, and documentation.

## Build 0.9.2 — Intelligent RFQ Engine

- Added flexible header recognition, canonical mapping, unit normalization, diagnostics, upload quality scoring, tests, and documentation.

## Build 0.9.1 — Multi-Category Foundation

- Added category routing, packaging/raw-material engine profiles, commodity metadata, selectors, guardrails, tests, and documentation.

## Build 0.8.1 — Deployment Stabilization

- Pinned Python 3.11 and exact dependencies and stabilized Streamlit deployment.

## Builds 0.1–0.8

Completed repository foundation, packaging intelligence, decision support, executive outputs, QA, CI, exports, portfolio assets, and public deployment.
