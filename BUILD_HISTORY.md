# Build History

## Build 0.9.2 — Intelligent RFQ Engine

**Status:** Completed — CI and Live Upload Validation Pending  
**Objective:** Accept varied supplier RFQ templates and convert them into a governed canonical schema.

### Completed

- Added intelligent header recognition and fuzzy mapping.
- Added canonical RFQ schema conversion.
- Added unit normalization and numeric conversion diagnostics.
- Added duplicate, missing-data, and unmapped-column analysis.
- Added RFQ upload quality scoring and validation messages.
- Integrated normalization into CSV and Excel loading.
- Added regression tests and documentation.
- Updated project governance records.

### Outcome

The application can now accept common variations such as Vendor Name, Unit Rate, Minimum Order Quantity, Delivery Days, Credit Terms, Delivery Terms, and UOM without requiring manual renaming. Weak or incomplete uploads remain visible and are blocked before supplier scoring when required information is missing.

### Next

Build 0.9.3 — Procurement Intelligence Engine.

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
