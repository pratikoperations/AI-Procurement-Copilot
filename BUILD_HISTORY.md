# Build History

## Version 1.0.1 — Governed Currency Display Maintenance

**Status:** Release candidate — documentation closure pending owner approval, merge, tag and GitHub release  
**Release basis:** Recovery R1 merged main SHA `18c009fd2947cf66dba564f0d063c726ffc45319`  
**Display-version correction:** current main SHA `ae50bca09e5cb33ed58439c6aecfcde4f391a846`

### Maintenance achievements
- Reconstructed the approved v1.0.1 currency-display maintenance on the canonical recovery-governance baseline.
- Added governed USD, INR and Both display handling across supported dashboards, Supplier Intelligence and exports.
- Corrected Supplier Intelligence risk-adjusted TCO source preservation during display rebuilding.
- Preserved canonical original, normalized, FX, unit and comparison-basis audit fields.
- Preserved supplier rankings, formulas, thresholds, recommendation eligibility and human approval controls.
- Preserved the existing single supplier selector and matching Supplier 360 profile path.
- Corrected displayed edition and build metadata to v1.0.1 and added release-version regression coverage.

### Validation evidence
- Standalone pre-maintenance main: 114 passed, 0 failed, 0 skipped, 1 warning; Streamlit smoke PASS.
- Reconstructed v1.0.1 candidate: 162 passed, 0 failed, 0 skipped, 1 warning; Streamlit smoke PASS.
- Final PR #9 Quality Checks: PASS.
- Recovery R1 hosted deployment startup: PASS.
- All six supplier profiles and USD/INR/Both modes manually accepted by the project owner.
- Primary `main` deployment after PR #9 manually accepted by the project owner.
- Unexpected display-version commit audited as limited to README, version manifest, app docstring, config metadata and a dedicated regression test.
- No procurement formula, schema, ranking, threshold, award-control, Version 1.1 or ERP implementation entered the release.

### Release result
- PR #9 merged to main as `18c009fd2947cf66dba564f0d063c726ffc45319`.
- Display-version correction merged separately as `ae50bca09e5cb33ed58439c6aecfcde4f391a846`.
- Release-closure documentation was reconstructed from current main to preserve both changes safely.
- Tag and GitHub release remain pending owner approval after closure PR review.

---

## Version 1.0.0 — Stable Portfolio Edition

**Status:** Released and frozen  
**Release basis:** Build 1.0 RC1.2.3

### Release achievements
- Packaging and Raw Material procurement engines
- Category-aware should-cost and TCO
- Risk, ESG, performance, innovation, financial, and SRM intelligence
- Procurement Intelligence and Supplier Intelligence
- Supplier 360 and recommendation governance
- Scenario stress testing and allocation
- Negotiation intelligence and executive outputs
- Business-readable and machine-readable exports
- Validation assurance, data confidence, and business-rule controls
- Green CI, Streamlit smoke testing, and direct export inspection

### Release result
- Critical defects open: 0
- Major defects open: 0
- Release Candidate Accepted
- Portfolio Edition v1.0.0 approved as Stable

### Next
Preserve the stable release. Version 1.1 remains a separate future-development stream.

---

## Build 1.0 RC1.2.3 — Scenario Engine Column Alignment Critical Hotfix

**Status:** Completed, CI validated, and live validated

- Aligned dashboard scenario rendering with governed annual-TCO headings.
- Resolved the live Multi-Scenario Stress Test `KeyError`.
- Added governed and legacy schema compatibility tests.

---

## Build 1.0 RC1.2.2 — Export Score Consistency and Scenario Integrity Hotfix

**Status:** Completed, CI validated, and manually validated

- Differentiated RFQ and governed Supplier Intelligence scores in readable exports.
- Corrected freight stress treatment for delivered-price suppliers.
- Added category-aware scenario TCO headings and terminology.

---

## Build 1.0 RC1.2.1 — Supplier 360 Display Formatting Hotfix

**Status:** Completed and CI validated

- Corrected character-by-character rendering of Approved Categories and Commodity Coverage.
- Added safe scalar and collection formatting with regression coverage.

---

## Build 1.0 RC1.2 — Export Integrity and Category-Aware Communication Hotfix

**Status:** Completed, CI validated, and manually validated

- Added currency, unit, communication, recommendation, classification, and export-governance controls.

---

## Build 1.0 RC1.1 — Final Executive Polish

**Status:** Completed

- Replaced technical chart labels and recommendation wording.
- Standardized category headings and executive terminology.

---

## Build 0.9.6.1 — Executive-Readable Supplier Intelligence UX Hotfix

**Status:** Completed — CI and live mobile validated

- Replaced raw structured output with executive-readable Supplier Intelligence.
- Added Financial, ESG, and Innovation evidence-governance safeguards.

---

## Build 0.9.6 — Independent Validation and Real-World Stress Testing

**Status:** Completed — CI validated

- Added data-confidence, eligibility, business-rule validation, adversarial tests, external-file validation and release governance.

---

## Earlier Builds
Completed repository foundation, category engines, executive outputs, Procurement Intelligence, Supplier Intelligence, CI, deployment, and validation governance.
