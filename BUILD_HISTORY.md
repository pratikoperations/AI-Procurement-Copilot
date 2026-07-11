# Build History

## Build 0.9.3.1 — Category Profile Integration Hotfix

**Status:** Implemented — CI and Live Deployment Validation Pending  
**Objective:** Remove the Streamlit startup failure caused by a missing `category_profile` key.

### Completed

- Added a reusable default category profile.
- Added profile completion and fallback logic.
- Guaranteed the sidebar return contract includes `category_profile`.
- Added defensive handling in `app.py`.
- Added hotfix regression tests and documentation.

### Outcome

The application no longer depends on an unguarded category-profile lookup and can recover safely when metadata is absent or incomplete.

### Next

Validate CI and live deployment before Build 0.9.4.

---

## Build 0.9.3 — Procurement Intelligence Engine

**Status:** Completed — CI Validated

- Added executive decision, strategy, allocation, negotiation, risk, scenario, explainability, dashboard, tests, and documentation.

---

## Build 0.9.2 — Intelligent RFQ Engine

**Status:** Completed — CI Validated

- Added intelligent header recognition, canonical mapping, unit normalization, diagnostics, upload quality scoring, tests, and documentation.

---

## Build 0.9.1 — Multi-Category Foundation

**Status:** Completed — CI Validated

- Added category routing, packaging and raw-material profiles, commodity metadata, selectors, guardrails, tests, and documentation.

---

## Build 0.8.1 — Deployment Stabilization

**Status:** Completed — Deployed Successfully

- Pinned Python 3.11 and stable dependencies and restored Streamlit Cloud stability.

---

## Builds 0.1–0.8

Completed repository foundation, packaging engines, decision intelligence, executive outputs, QA, CI, exports, portfolio assets, and public deployment.
