# Build History

## Build 1.0 RC1.2.2 — Export Score Consistency and Scenario Integrity Hotfix

**Status:** Implementation completed — CI, Streamlit, and manual retest pending  
**Objective:** Correct readable score ambiguity, freight-scenario integrity, and residual risk terminology defects.

### Completed

- Differentiated RFQ and governed Supplier Intelligence scores in readable exports.
- Added governed Supplier 360 score fields to readable supplier score reports.
- Corrected freight stress treatment for delivered-price suppliers.
- Added category-aware scenario TCO headings.
- Replaced Risk Score with Risk Resilience Score in readable scenario exports.
- Added Packaging and Raw Material freight-scenario regression tests.
- Preserved feature freeze and existing score weightings.

### Remaining gates

- Latest GitHub Actions green
- Streamlit smoke test
- Manual Supplier Scores Report retest
- Manual Scenarios worksheet retest
- Confirmation that Freight +50% changes unit and annual TCO
- Closure of RC1-DEF-012 through RC1-DEF-014
- Final release approval

### Next

Validate RC1.2.2. Do not tag v1.0.0 and do not add features.

---

## Build 1.0 RC1.2.1 — Supplier 360 Display Formatting Hotfix

**Status:** Completed and CI validated

- Corrected character-by-character rendering of Approved Categories and Commodity Coverage.
- Added safe scalar and collection formatting with regression coverage.

---

## Build 1.0 RC1.2 — Export Integrity and Category-Aware Communication Hotfix

**Status:** Completed and CI validated; manual download validation continued

- Added currency, unit, communication, recommendation, classification, and export-governance controls.

---

## Build 1.0 RC1.1 — Final Executive Polish

**Status:** Implemented

- Replaced technical chart labels and recommendation wording.
- Standardized category headings and executive terminology.

---

## Build 0.9.6.1 — Executive-Readable Supplier Intelligence UX Hotfix

**Status:** Completed — CI and live mobile validated

- Replaced raw structured output with executive-readable Supplier Intelligence.
- Added Financial, ESG, and Innovation evidence-governance safeguards.

---

## Build 0.9.6 — Independent Validation and Real-World Stress Testing

**Status:** Completed — CI Validated through Quality Checks #150–#208

- Added data-confidence, eligibility, business-rule validation, adversarial tests, external-file validation and release governance.

---

## Earlier Builds

Completed repository foundation, category engines, executive outputs, Procurement Intelligence, Supplier Intelligence, CI, deployment, and validation governance.
