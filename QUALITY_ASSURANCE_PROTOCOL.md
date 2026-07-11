# Quality Assurance Protocol

## Purpose

This protocol defines the technical, procurement, data-quality, currency, unit, model-risk, export, executive-UX, and release gates for AI Procurement Copilot.

## Build Quality Gates

| Gate | Check | Pass criteria |
|---|---|---|
| G1 | GitHub record | All meaningful changes committed and recoverable |
| G2 | App startup | `streamlit run app.py` launches without errors |
| G3 | Imports | All modules import successfully |
| G4 | Functional test | Packaging and Raw Material demos work |
| G5 | Regression test | Previous functionality remains intact |
| G6 | Procurement logic | Outputs are commercially sensible, traceable and explainable |
| G7 | Data confidence | Missing, defaulted and inferred data is visible |
| G8 | Currency integrity | Original and normalized values are explicit; unsupported conversion blocks |
| G9 | Unit integrity | Category unit is explicit; PET Resin uses kg |
| G10 | Recommendation safety | Invalid or insufficient data cannot produce final award language |
| G11 | Evidence governance | Financial, ESG and Innovation conclusions are capped by evidence |
| G12 | Classification precedence | Exit Candidate cannot also receive contradictory development or long-term roles |
| G13 | Allocation feasibility | Allocation totals 100% and remains within capacity |
| G14 | Communication consistency | Memo, email, narrative and screen share eligibility status |
| G15 | Export integrity | Readable reports use business headings and match on-screen values |
| G16 | Audit separation | Machine-readable data remains separate from readable reports |
| G17 | Executive UX | No raw payload or snake_case is visible in business outputs |
| G18 | Mobile usability | Cards, charts, selectors and matrices remain usable on mobile |
| G19 | Documentation | Status, changelog, history, version, QA and evidence updated |
| G20 | Independent review | External AI and human findings are dispositioned |
| G21 | Recovery | Project can be resumed from GitHub alone |

## RC1.2 Required Controls

Before accepting Build 1.0 RC1.2, verify:

- Standard Packaging and Raw Material demo rows contain explicit currency and unit.
- Standard PET Resin demo contains only USD comparison values and kg units.
- INR quotations convert to USD only with a positive INR-per-USD rate.
- Unsupported currency conversion blocks processing.
- No USD-labelled field contains an unconverted INR value.
- Supplier email content changes by category.
- Blocked, Insufficient Data, Human Review Required, Eligible With Conditions, and Eligible language is consistent across outputs.
- Recommendation roles use governed displayed scores and evidence status.
- Most Innovative and Most Sustainable return No Qualified Supplier when evidence is insufficient.
- Best Strategic Partner and Best Long-Term Supplier require sufficient evidence and cannot select an Exit Candidate.
- Exit Candidate and Development Candidate are not assigned to the same supplier.
- Risk Resilience Score is used in visible business outputs.
- Supplier Scores Report and Supplier Comparison Report contain human-readable headings.
- Excel readable sheets and audit sheets are clearly separated.
- Existing and new tests pass.
- Streamlit smoke test passes.
- Every downloadable file is opened and manually reviewed.

## Portfolio Edition v1.0 Acceptance Criteria

- Packaging and Raw Material workflows run end to end.
- No open Critical defect remains.
- No unmitigated Major defect remains.
- GitHub Actions are green.
- Streamlit smoke and manual deployment checks pass.
- Download-content audit passes.
- Allocation feasibility is 10/10.
- Recommendation safety is at least 9/10.
- Executive UX is at least 9/10.
- Independent reviews are completed or formally waived with residual-risk acceptance.
- Final release-readiness score is at least 9.0/10.

## Defect Governance

Every accepted Critical or Major finding requires a defect-register entry, reproduction steps, corrective commit, regression test, retest evidence, and release-blocker decision. Rejected findings require written rationale.

## Governance Principle

No release is complete until code, screen outputs, communications, and downloadable reports tell the same validated story.
