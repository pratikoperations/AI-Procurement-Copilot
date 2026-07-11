# Build History

## Build 1.0 RC1.2 — Export Integrity and Category-Aware Communication Hotfix

**Status:** Implementation completed — CI, Streamlit, and manual download retest pending  
**Objective:** Correct release-blocking inconsistencies between screen outputs, supplier communications, recommendation rankings, and downloadable reports.

### Completed

- Added original and normalized currency governance.
- Added explicit FX rate, UOM, and comparison basis.
- Corrected synthetic demo metadata and standardized PET Resin to kg.
- Added category-aware and eligibility-aware supplier communication.
- Governed recommendation roles using displayed scores and evidence status.
- Prevented unsupported ESG, innovation, strategic-partner, and long-term awards.
- Enforced Exit Candidate and Development Candidate separation.
- Renamed visible risk terminology to Risk Resilience Score.
- Added readable supplier score and comparison exports.
- Preserved separate machine-readable audit exports.
- Added six focused regression-test files and download content audit documentation.

### Remaining gates

- Latest RC1.2 GitHub Actions green
- Streamlit smoke test for Packaging and Raw Material
- Manual opening and review of all report downloads
- Closure of RC1-DEF-005 through RC1-DEF-011 after retest
- Independent reviews completed or formally waived
- Final `v1.0.0` release approval

### Next

Validate RC1.2. Do not tag v1.0.0 and do not add features.

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
