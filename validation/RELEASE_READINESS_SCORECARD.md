# Release Readiness Scorecard

## Current status

**Build 0.9.6 implementation in progress. Scores below are provisional until CI, live deployment, Gemini, Perplexity and human review are complete.**

| Dimension | Target | Provisional score | Evidence / remaining action |
|---|---:|---:|---|
| Formula correctness | ≥9.0 | 8.8 | Formula register created; independent review pending |
| Input validation | ≥9.0 | 9.1 | Critical field, range, currency, UOM and volume gates implemented; CI pending |
| Category logic | ≥9.0 | 9.2 | Packaging and raw-material routes covered by regression tests |
| Recommendation safety | ≥9.0 | 9.1 | Eligibility gate and narrative withholding implemented; live test pending |
| Allocation feasibility | 10.0 | 9.5 | 100% and capacity checks added; independent stress review pending |
| External-file robustness | ≥8.5 | 8.8 | 14 synthetic files and file tests added; actual anonymized user files pending |
| Data-confidence transparency | ≥9.0 | 9.3 | Supplied, defaulted, inferred and missing-critical percentages visible |
| Explainability | ≥9.0 | 9.4 | Rules, assumptions, gates and withheld outcomes visible |
| Supplier intelligence integrity | ≥9.0 | 8.9 | Default penalty added; external and human review pending |
| Documentation | ≥9.0 | 9.1 | Registers, matrix, model-risk and QA documentation added |
| Regression coverage | ≥9.0 | 9.0 | Safety, adversarial and file tests added; CI pending |
| Live deployment stability | ≥9.0 | 8.5 | Manual Streamlit validation pending |

**Provisional average:** 9.1/10

## Release blockers

- Latest Build 0.9.6 GitHub Actions must be green.
- Streamlit deployment and both category workflows must be manually validated.
- Gemini review must be completed and dispositioned.
- Perplexity method review must be completed and dispositioned.
- Human procurement review must be completed or formally waived with written reason.
- All Critical defects must be closed and retested.
- No unmitigated Major defect may remain.

## Approval

Portfolio Edition v1.0 is **not yet approved**. This scorecard becomes final only after evidence links and reviewer dispositions are recorded.
