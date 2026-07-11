# Quality Assurance Protocol

## Purpose

This protocol defines the technical, procurement, data-quality, model-risk and release gates for every AI Procurement Copilot build.

## Build Quality Gates

| Gate | Check | Pass criteria |
|---|---|---|
| G1 | GitHub record | All meaningful changes committed and recoverable |
| G2 | App startup | `streamlit run app.py` launches without errors |
| G3 | Imports | All modules import successfully |
| G4 | Functional test | New features work with category-appropriate demo data |
| G5 | Regression test | Previous functionality remains intact |
| G6 | Code quality | Modular, readable and without obvious duplicated logic |
| G7 | Procurement logic | Outputs are commercially sensible, traceable and explainable |
| G8 | Data confidence | Missing, defaulted and inferred data is visible |
| G9 | Recommendation safety | Invalid or insufficient data cannot produce final award language |
| G10 | Allocation feasibility | Allocation totals 100% and does not exceed verified capacity |
| G11 | External files | Canonical, alternate, incomplete, invalid and large files behave as expected |
| G12 | Documentation | Status, changelog, history, version, QA and validation evidence updated |
| G13 | Independent review | External AI and human findings are dispositioned |
| G14 | Recovery | Project can be resumed from GitHub alone |

## Scoring Framework

Score each build from 0–10 across:

- Architecture
- Code quality
- Formula correctness
- Procurement logic
- Input validation
- Recommendation safety
- Allocation feasibility
- External-file robustness
- Data-confidence transparency
- Explainability
- User experience
- Documentation
- Interview readiness
- Maintainability
- Live deployment stability

## Minimum Acceptance Threshold

Normal build target: **8.5/10** or higher.

Portfolio Edition v1.0 release target: **9.0/10** or higher, with allocation feasibility at **10/10** and recommendation safety at **9/10** or higher.

## Build 0.9.6 Required Controls

Before displaying a final recommendation, verify:

- Required RFQ data is valid.
- Quoted price and annual volume are positive.
- Percentages and operational metrics are within valid ranges.
- Currency and UOM are explicit and consistent.
- Supplier capacity meets demand.
- Allocation totals 100% and is supplier-feasible.
- At least one supplier meets the configured risk threshold.
- Data-confidence status is visible.
- Recommendation eligibility is visible.
- Blocked and insufficient-data cases withhold final award language.
- Demo data is distinguished from uploaded unverified data.

## Release v1.0 Acceptance Criteria

- Packaging and Raw Material workflows run end to end.
- Supplier Intelligence and Procurement Intelligence remain functional.
- Realistic and adversarial file tests pass.
- Formula, assumption and decision-rule registers are current.
- No open Critical defects remain.
- No unmitigated Major defects remain.
- GitHub Actions are green.
- Streamlit smoke and manual deployment checks pass.
- Gemini independent validation is completed and dispositioned.
- Perplexity methodology validation is completed and dispositioned.
- Human procurement review is completed or formally waived with written residual-risk acceptance.
- Final release-readiness score is at least 9.0/10.

## Defect Governance

Every accepted Critical or Major finding requires:

1. Defect-register entry
2. Reproduction steps
3. Corrective commit
4. Regression test
5. Retest evidence
6. Release-blocker decision

Rejected findings require written rationale.

## Governance Principle

No feature or release is complete until it is committed, tested, documented, recoverable, independently challenged and approved under human procurement governance.
