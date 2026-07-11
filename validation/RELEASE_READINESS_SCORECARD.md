# Release Readiness Scorecard

## Current status

**Build 0.9.6 implementation and CI validation are complete. Scores remain provisional until live deployment, Gemini, Perplexity and human review are complete.**

| Dimension | Target | Provisional score | Evidence / remaining action |
|---|---:|---:|---|
| Formula correctness | ≥9.0 | 8.8 | Formula register created; independent review pending |
| Input validation | ≥9.0 | 9.4 | Critical field, range, currency, UOM and volume gates passed CI |
| Category logic | ≥9.0 | 9.3 | Packaging and raw-material routes passed regression tests |
| Recommendation safety | ≥9.0 | 9.4 | Eligibility gate and narrative withholding passed CI; live test pending |
| Allocation feasibility | 10.0 | 9.7 | 100% and capacity checks passed CI; manual stress review pending |
| External-file robustness | ≥8.5 | 9.0 | Fourteen synthetic files and file tests passed CI; real anonymized files pending |
| Data-confidence transparency | ≥9.0 | 9.4 | Supplied, defaulted, inferred and missing-critical percentages visible and tested |
| Explainability | ≥9.0 | 9.4 | Rules, assumptions, gates and withheld outcomes visible |
| Supplier intelligence integrity | ≥9.0 | 9.0 | Default penalty passed CI; external and human review pending |
| Documentation | ≥9.0 | 9.3 | Registers, matrix, model-risk and QA documentation complete |
| Regression coverage | ≥9.0 | 9.4 | Quality Checks #150–#208 confirmed green |
| Live deployment stability | ≥9.0 | 8.5 | Manual Streamlit validation pending |

**Provisional average:** 9.2/10

## Confirmed evidence

- GitHub Quality Checks #150–#208: Green, confirmed by project owner
- All internally identified Build 0.9.6 Critical and Major defects: Closed and CI retested
- Safety, adversarial and synthetic external-file tests: Passing in CI

## Remaining release blockers

- Streamlit deployment and both category workflows must be manually validated.
- Gemini review must be completed and dispositioned.
- Perplexity method review must be completed and dispositioned.
- Human procurement review must be completed or formally waived with written reason.
- External reviews must confirm no new open Critical defect or unmitigated Major defect.
- Allocation feasibility must reach the required final 10/10 after live/manual evidence.

## Approval

Portfolio Edition v1.0 is **not yet approved**. The scorecard becomes final only after live evidence and reviewer dispositions are recorded.
