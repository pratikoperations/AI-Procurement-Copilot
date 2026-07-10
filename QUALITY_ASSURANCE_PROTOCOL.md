# Quality Assurance Protocol

## Purpose

This protocol defines the quality gate for every AI Procurement Copilot build.

## Build Quality Gates

Every build must be assessed against the following gates before moving to the next build.

| Gate | Check | Pass Criteria |
|---|---|---|
| G1 | GitHub Commit | All meaningful changes committed to GitHub |
| G2 | App Runs | `streamlit run app.py` launches without errors |
| G3 | Imports | All modules import successfully |
| G4 | Functional Test | New features work with synthetic demo data |
| G5 | Regression Test | Previous build features still work |
| G6 | Code Quality | Modular, readable, no obvious duplicate logic |
| G7 | Procurement Logic | Outputs are commercially sensible and explainable |
| G8 | Interview Quality | Feature can be explained in a senior procurement interview |
| G9 | Documentation | PROJECT_STATUS, CHANGELOG, BUILD_HISTORY updated |
| G10 | Recovery | Project can be resumed from GitHub alone |

## Scoring Framework

Each completed build should be reviewed across:

- Architecture: /10
- Code Quality: /10
- Procurement Logic: /10
- User Experience: /10
- Documentation: /10
- Interview Readiness: /10
- Maintainability: /10

## Minimum Acceptance Threshold

Target score: **8.5 / 10** or higher.

If a build falls below 8.5, create a remediation task before proceeding to the next major release milestone.

## Release v1.0 Acceptance Criteria

Before Portfolio Edition v1.0 release:

- App runs end-to-end with synthetic demo data.
- RFQ upload works with the sample CSV.
- Should-cost model is visible and auditable.
- TCO output is explainable.
- Risk assumptions are visible.
- ESG and performance scoring are visible.
- Lowest-price vs best-value logic is clear.
- Allocation recommendation is visible.
- Scenario stress test works.
- Negotiation playbook is generated.
- Executive memo is generated.
- Supplier email is generated.
- AI explainability panel is generated.
- Interview talking points are available.
- Documentation is updated.
- Recovery manifest is current.

## Governance Principle

No feature is considered complete until it is committed, documented, and recoverable from GitHub.
