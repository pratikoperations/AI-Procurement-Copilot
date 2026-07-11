# Quality Assurance Protocol

## Purpose

This protocol defines the technical, procurement, data-quality, model-risk, executive-UX and release gates for every AI Procurement Copilot build.

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
| G12 | Executive UX | No raw structured payload, code-style field name or debug object is visible |
| G13 | Evidence governance | Financial, ESG and innovation conclusions are capped by evidence completeness |
| G14 | Mobile usability | Cards, charts, selectors and matrices remain usable on mobile |
| G15 | Documentation | Status, changelog, history, version, QA and validation evidence updated |
| G16 | Independent review | External AI and human findings are dispositioned |
| G17 | Recovery | Project can be resumed from GitHub alone |

## Scoring Framework

Score each build from 0–10 across architecture, code quality, formula correctness, procurement logic, input validation, recommendation safety, allocation feasibility, external-file robustness, data-confidence transparency, evidence integrity, explainability, executive UX, mobile usability, documentation, interview readiness, maintainability and live deployment stability.

## Minimum Acceptance Threshold

Normal build target: **8.5/10** or higher.

Portfolio Edition v1.0 release target: **9.0/10** or higher, with allocation feasibility at **10/10**, recommendation safety at **9/10** or higher, and executive UX at **9/10** or higher.

## Build 0.9.6 Required Controls

Before displaying a final recommendation, verify valid RFQ data, positive price and volume, valid ranges, consistent currency and UOM, sufficient capacity, feasible allocation, risk threshold, visible data confidence, visible eligibility, safe narrative withholding and explicit demo/upload source status.

## Build 0.9.6.1 Required Controls

Before accepting the Supplier Intelligence UX hotfix, verify:

- No `st.json` or equivalent structured-data renderer remains in application UI files.
- No raw dictionary, raw list, braces, quoted field names or snake-case business labels appear on-screen.
- Performance uses readable scorecards, chart, strengths, gaps and actions.
- Financial uses governed displayed score, completeness, assessment status, evidence and due-diligence warning.
- ESG uses governed displayed score, completeness, maturity cap, document requirements and corrective actions.
- Innovation uses governed displayed score, completeness, maturity cap, opportunity matrix and agenda.
- SRM uses classification, rationale, strategy and governance matrix.
- Supplier 360 profile is readable on mobile.
- Machine-readable audit data is download-only.
- A readable Supplier 360 report is available.
- Packaging and Raw Material workflows remain functional.
- New and existing tests pass.

## Release v1.0 Acceptance Criteria

- Packaging and Raw Material workflows run end to end.
- Supplier Intelligence and Procurement Intelligence remain functional.
- Realistic and adversarial file tests pass.
- Formula, assumption and decision-rule registers are current.
- No open Critical defects remain.
- No unmitigated Major defects remain.
- GitHub Actions are green.
- Streamlit smoke and manual deployment checks pass.
- Executive-readable outputs pass mobile review.
- Gemini independent validation is completed and dispositioned.
- Perplexity methodology validation is completed and dispositioned.
- Human procurement review is completed or formally waived with written residual-risk acceptance.
- Final release-readiness score is at least 9.0/10.

## Defect Governance

Every accepted Critical or Major finding requires a defect-register entry, reproduction steps, corrective commit, regression test, retest evidence and release-blocker decision. Rejected findings require written rationale.

## Governance Principle

No feature or release is complete until it is committed, tested, documented, recoverable, independently challenged and approved under human procurement governance.
