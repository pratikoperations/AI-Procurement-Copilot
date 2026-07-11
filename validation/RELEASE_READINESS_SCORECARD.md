# Release Readiness Scorecard

## Current status

**Build 1.0 RC1.1 implementation is complete. Build 0.9.6.1 CI and live mobile validation passed. Latest RC1.1 CI, live polish retest, export inspection, and independent review gates remain open.**

| Dimension | Target | Provisional score | Evidence / remaining action |
|---|---:|---:|---|
| Formula correctness | ≥9.0 | 8.8 | Formula register created; independent review pending |
| Input validation | ≥9.0 | 9.4 | Critical field, range, currency, UOM and volume gates passed CI |
| Category logic | ≥9.0 | 9.5 | Packaging and Raw Material routes live validated; Raw Material safety block observed |
| Recommendation safety | ≥9.0 | 9.6 | Eligibility and narrative withholding passed CI and live review |
| Allocation feasibility | 10.0 | 9.7 | Capacity checks passed CI; final manual stress evidence pending |
| External-file robustness | ≥8.5 | 9.0 | Synthetic file tests passed; real anonymized files remain optional future evidence |
| Data-confidence transparency | ≥9.0 | 9.5 | Supplied, defaulted, inferred, and missing-critical percentages visible |
| Explainability | ≥9.0 | 9.7 | Executive-readable evidence, recommendation rationale, and governance presentation implemented |
| Supplier intelligence integrity | ≥9.0 | 9.6 | Financial, ESG, and Innovation evidence caps passed CI and live screenshots |
| Executive UX | ≥9.0 | 9.7 | Raw payloads removed; chart and recommendation terminology polished in RC1.1 |
| Documentation | ≥9.0 | 9.6 | Status, changelog, history, manifest, defects, and RC1 records updated |
| Regression coverage | ≥9.0 | 9.6 | UI, evidence-governance, and executive-terminology tests included |
| Live deployment stability | ≥9.0 | 9.3 | Packaging and Raw Material screens loaded on mobile; RC1.1 redeploy retest pending |

**Provisional average:** 9.5/10

## Confirmed evidence

- GitHub Quality Checks #150–#208: Green for Build 0.9.6.
- Build 0.9.6.1 latest Quality Checks through #230: Green except superseded historical run #220.
- Streamlit Packaging and Raw Material routes loaded successfully on Android / Chrome.
- Financial, ESG, Innovation, SRM, Performance, Supplier Intelligence, and safety-gate outputs were manually reviewed.
- VAL-001 through VAL-009: Closed.
- No open Critical, Major, or Moderate defect remains.

## RC1.1 fixed findings

- RC1-UX-001: Technical chart legends — fixed; retest pending.
- RC1-UX-002: Developer-style recommendation explanation — fixed; retest pending.
- RC1-UX-003: Packaging heading shown in Raw Material Cost & Risk — fixed; retest pending.

## Remaining release blockers

- Latest Build 1.0 RC1.1 GitHub Actions must be green.
- Streamlit must show the RC1.1 build label and polished chart/recommendation wording.
- Excel, CSV, TXT, and audit-data downloads must be opened successfully.
- Gemini review must be completed and dispositioned.
- Perplexity methodology review must be completed and dispositioned.
- Human procurement review must be completed or formally waived.
- Allocation feasibility must reach final 10/10 after manual stress evidence.

## Approval

Portfolio Edition v1.0 is **release-candidate ready but not yet tagged**. Final approval follows the remaining gates above.
