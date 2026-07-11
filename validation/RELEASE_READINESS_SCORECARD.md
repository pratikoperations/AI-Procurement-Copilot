# Release Readiness Scorecard

## Current status

**Build 1.0 RC1.2.2 implementation is complete. CI, Streamlit smoke testing, corrected export inspection, and independent review remain open. Scores are provisional until those gates close.**

| Dimension | Target | Provisional score | Evidence / remaining action |
|---|---:|---:|---|
| Formula correctness | ≥9.0 | 9.0 | Freight-scenario defect corrected; independent review pending |
| Input validation | ≥9.0 | 9.5 | Price, volume, currency, UOM, percentage, capacity and allocation controls implemented |
| Currency and unit integrity | ≥9.0 | 9.5 | Original/normalized fields and category units validated; final download retest pending |
| Category logic | ≥9.0 | 9.6 | Packaging and Raw Material logic preserved; category-aware communication active |
| Recommendation safety | ≥9.0 | 9.7 | Eligibility-aware outputs and unsupported-role withholding implemented |
| Allocation feasibility | 10.0 | 9.7 | Automated checks passed historically; final manual stress evidence pending |
| External-file robustness | ≥8.5 | 9.0 | Synthetic file tests available; final external-file review pending |
| Data-confidence transparency | ≥9.0 | 9.5 | Supplied, defaulted, inferred and missing-critical percentages visible |
| Evidence governance | ≥9.0 | 9.7 | Financial, ESG, Innovation and long-term role qualification governed |
| Cross-output consistency | ≥9.0 | 9.4 | RFQ and governed scores explicitly differentiated; corrected export retest pending |
| Executive UX | ≥9.0 | 9.7 | Raw payloads removed; executive terminology active |
| Export integrity | ≥9.0 | 9.3 | Score labels and scenario headings corrected; files must be reopened |
| Scenario integrity | ≥9.0 | 9.2 | Freight pass-through correction and regression tests added; CI/manual retest pending |
| Documentation | ≥9.0 | 9.8 | RC1.2.2 hotfix and defect governance updated |
| Regression coverage | ≥9.0 | 9.8 | New export and scenario integrity tests added |
| Live deployment stability | ≥9.0 | 9.0 | Prior app stable; RC1.2.2 redeployment smoke test pending |

**Provisional average:** 9.4/10

## Confirmed evidence

- Builds through RC1.2.1 have recorded green CI.
- Financial, ESG, Innovation, SRM, Performance and Supplier Intelligence were manually reviewed.
- RC1.2.2 corrective code and tests are committed.
- Feature freeze remains active.

## RC1.2.2 release blockers

- Latest GitHub Actions must be green.
- Streamlit must load Build 1.0 RC1.2.2 successfully.
- Freight +50% must increase unit and annual TCO for PET Resin and Packaging demos.
- Supplier Scores Report must clearly distinguish RFQ and governed Supplier Intelligence scores.
- Scenario worksheet must use Risk Resilience Score and category-aware TCO headings.
- Corrected Excel, CSV, TXT and audit downloads must be opened and inspected.
- Screen, memo, email, narrative and exports must share the same eligibility status.
- RC1-DEF-012 through RC1-DEF-014 must be closed after retest.
- Independent reviews must be completed or formally waived.
- Allocation feasibility must reach final 10/10.

## Approval

Portfolio Edition v1.0 is **not yet approved or tagged**. RC1.2.2 must pass CI, live smoke testing and corrected download-content validation first.
