# Build History

## Build 0.9.6.1 — Executive-Readable Supplier Intelligence UX Hotfix

**Status:** Implementation completed — CI and live validation pending  
**Objective:** Remove developer-style structured output and align displayed supplier intelligence with evidence quality.

### Completed

- Added reusable executive UI components.
- Replaced raw structured Supplier Intelligence output with cards, score matrices, charts, evidence lists and action plans.
- Added financial evidence-completeness governance and score caps.
- Added ESG evidence-completeness governance and maturity caps.
- Added innovation evidence-completeness governance and maturity caps.
- Added readable Supplier 360 report download.
- Retained machine-readable audit data as download-only.
- Added UI-output and evidence-governance regression tests.
- Recorded VAL-006 to VAL-009.

### Outcome

Supplier Intelligence now presents procurement meaning rather than internal object structure. Low-evidence financial, ESG and innovation results are explicitly provisional and cannot appear as verified leading performance.

### Remaining gates

- Green Build 0.9.6.1 GitHub Actions
- Streamlit smoke test
- Live Packaging Supplier Intelligence validation
- Live Raw Material Supplier Intelligence validation
- Closure of VAL-006 to VAL-009 after retest
- Gemini, Perplexity and human review

### Next

Validate Build 0.9.6.1. Build 1.0 remains blocked.

---

## Build 0.9.6 — Independent Validation and Real-World Stress Testing

**Status:** Completed — CI Validated through Quality Checks #150–#208

- Added data-confidence, eligibility, business-rule validation, adversarial tests, external-file validation and release governance.

---

## Build 0.9.5 — Supplier Intelligence Platform

**Status:** Completed — CI Validated

- Added Supplier 360, performance, financial, ESG, innovation, SRM, comparison, recommendations, narratives, exports and tests.

---

## Build 0.9.4 — Category-Specific Cost and Risk Engines

**Status:** Completed — CI Validated

- Added production raw-material should-cost, risk, TCO, scoring and routing.

---

## Builds 0.1–0.9.3.1

Completed repository foundation, packaging engines, executive outputs, QA, CI, exports, deployment, multi-category architecture, Intelligent RFQ, Procurement Intelligence and stabilization hotfixes.
