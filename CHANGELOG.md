# Changelog

All meaningful project changes are recorded here.

## Build 0.9.4 — Category-Specific Cost and Risk Engines

### Added

- Production raw-material should-cost engine.
- Commodity-aware raw-material risk model.
- Delivered, working-capital, duty, volatility, and risk-adjusted raw-material TCO.
- Category-aware supplier scoring weights and engine routing.
- Raw-material synthetic demo data for supported commodities.
- Category should-cost router.
- Active Raw Material Procurement workflow in Streamlit.
- Category-specific regression tests and documentation.

### Changed

- Raw Material Procurement promoted from Foundation Preview to Active.
- Category selection now controls demo data, should-cost, TCO, risk, and scoring.

### QA Notes

- Existing packaging tests remain part of the regression suite.
- New raw-material tests added.
- CI and live multi-category validation are pending.

## Build 0.9.3.1 — Category Profile Integration Hotfix

- Eliminated the startup `category_profile` error and preserved explicit category units.
- CI validated.

## Build 0.9.3 — Procurement Intelligence Engine

- Added executive decision, strategy, allocation, negotiation, risk, scenario, explainability, dashboard, tests, and documentation.

## Build 0.9.2 — Intelligent RFQ Engine

- Added flexible header recognition, canonical mapping, unit normalization, diagnostics, upload quality scoring, tests, and documentation.

## Build 0.9.1 — Multi-Category Foundation

- Added category routing, packaging/raw-material engine profiles, commodity metadata, selectors, guardrails, tests, and documentation.

## Builds 0.1–0.8.1

Completed repository foundation, packaging intelligence, executive outputs, QA, CI, exports, deployment, and stabilization.
