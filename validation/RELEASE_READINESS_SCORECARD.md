# Release Readiness Scorecard

## Current status

**Build 0.9.6 was CI validated. Build 0.9.6.1 implementation is complete but its CI and live UX validation remain pending. Scores are provisional until hotfix, Gemini, Perplexity and human-review evidence is complete.**

| Dimension | Target | Provisional score | Evidence / remaining action |
|---|---:|---:|---|
| Formula correctness | ≥9.0 | 8.8 | Formula register created; independent review pending |
| Input validation | ≥9.0 | 9.4 | Critical field, range, currency, UOM and volume gates passed Build 0.9.6 CI |
| Category logic | ≥9.0 | 9.3 | Packaging and raw-material routes passed Build 0.9.6 tests; hotfix retest pending |
| Recommendation safety | ≥9.0 | 9.4 | Eligibility and narrative withholding passed CI; live test pending |
| Allocation feasibility | 10.0 | 9.7 | Capacity checks passed CI; manual stress review pending |
| External-file robustness | ≥8.5 | 9.0 | Synthetic file tests passed Build 0.9.6 CI; real anonymized files pending |
| Data-confidence transparency | ≥9.0 | 9.4 | Supplied, defaulted, inferred and missing-critical percentages visible |
| Explainability | ≥9.0 | 9.5 | Executive-readable evidence, status and governance presentation implemented |
| Supplier intelligence integrity | ≥9.0 | 9.2 | Financial, ESG and innovation evidence caps implemented; CI/live retest pending |
| Executive UX | ≥9.0 | 9.2 | Raw structured output removed; cards, charts and matrices added; live mobile review pending |
| Documentation | ≥9.0 | 9.4 | UX standard, UI audit, hotfix record and defects updated |
| Regression coverage | ≥9.0 | 9.4 | UI and evidence-governance tests added; Build 0.9.6.1 CI pending |
| Live deployment stability | ≥9.0 | 8.7 | Prior deployment starts; hotfix redeployment validation pending |

**Provisional average:** 9.2/10

## Confirmed evidence

- GitHub Quality Checks #150–#208: Green for Build 0.9.6, confirmed by project owner
- Build 0.9.6 safety, adversarial and synthetic-file tests: Passed
- Build 0.9.6.1 code and documentation: Committed
- VAL-006 to VAL-009: Corrective implementation completed

## Remaining release blockers

- Build 0.9.6.1 GitHub Actions must be green.
- Streamlit smoke test must pass after redeployment.
- Packaging and Raw Material Supplier Intelligence must be visually validated on mobile.
- VAL-006 to VAL-009 must be marked closed after retest.
- Gemini review must be completed and dispositioned.
- Perplexity method review must be completed and dispositioned.
- Human procurement review must be completed or formally waived.
- No new Critical or unmitigated Major defect may remain.
- Allocation feasibility must reach final 10/10 after live/manual evidence.

## Approval

Portfolio Edition v1.0 is **not yet approved**. The scorecard becomes final only after hotfix CI, live evidence and reviewer dispositions are recorded.
