# Release Readiness Scorecard

## Current status

**Build 1.0 RC1.2 implementation is complete. CI, Streamlit smoke testing, manual download inspection, and independent review remain open. Scores are provisional until those gates close.**

| Dimension | Target | Provisional score | Evidence / remaining action |
|---|---:|---:|---|
| Formula correctness | ≥9.0 | 8.8 | Formula register complete; independent review pending |
| Input validation | ≥9.0 | 9.5 | Price, volume, currency, UOM, percentage, capacity and allocation controls implemented |
| Currency and unit integrity | ≥9.0 | 9.4 | Original/normalized fields and FX governance implemented; live/download retest pending |
| Category logic | ≥9.0 | 9.6 | Packaging and Raw Material logic preserved; category-aware communication added |
| Recommendation safety | ≥9.0 | 9.7 | Eligibility-aware outputs and unsupported-role withholding implemented |
| Allocation feasibility | 10.0 | 9.7 | Automated checks passed historically; final manual stress evidence pending |
| External-file robustness | ≥8.5 | 9.0 | Synthetic file tests available; RC1.2 currency cases added |
| Data-confidence transparency | ≥9.0 | 9.5 | Supplied, defaulted, inferred and missing-critical percentages visible |
| Evidence governance | ≥9.0 | 9.7 | Financial, ESG, Innovation and long-term role qualification governed |
| Cross-output consistency | ≥9.0 | 9.3 | Memo, email, narrative and audit status integrated; manual download review pending |
| Executive UX | ≥9.0 | 9.7 | Raw payloads removed; business terminology and Risk Resilience Score used |
| Export integrity | ≥9.0 | 9.2 | Readable report builders and audit separation implemented; files must be opened |
| Documentation | ≥9.0 | 9.7 | RC1.2 hotfix, currency, communication and download-audit docs created |
| Regression coverage | ≥9.0 | 9.7 | Six new RC1.2 test files added plus existing suite |
| Live deployment stability | ≥9.0 | 9.0 | Prior app stable; RC1.2 redeployment smoke test pending |

**Provisional average:** 9.4/10

## Confirmed evidence

- Builds through 0.9.6.1 have recorded green CI and live validation.
- Financial, ESG, Innovation, SRM, Performance and Supplier Intelligence were manually reviewed.
- RC1.2 corrective code and tests are committed.
- Feature freeze remains active.

## RC1.2 release blockers

- Latest GitHub Actions must be green.
- Standard PET Resin demo must load without false mixed-currency blocking.
- PET Resin email must use kg and raw-material terminology.
- Recommendation rankings must show No Qualified Supplier when evidence is insufficient.
- Exit Candidate and Development Candidate must be assigned to different suppliers.
- Excel, CSV, TXT and audit downloads must be opened and inspected.
- Screen, memo, email, narrative and exports must share the same eligibility status.
- RC1-DEF-005 through RC1-DEF-011 must be closed after retest.
- Independent reviews must be completed or formally waived.
- Allocation feasibility must reach final 10/10.

## Approval

Portfolio Edition v1.0 is **not yet approved or tagged**. RC1.2 must pass CI, live smoke testing and download-content validation first.
