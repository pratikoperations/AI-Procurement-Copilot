# Project Status

## Repository
`pratikoperations/AI-Procurement-Copilot`

## Canonical Stable Branch
`main`

## Verified Main SHA
`39bfc2d0c75e58c883fdcec797f66dff2edd9eec`

## Stable Release
- Release: Portfolio Edition v1.0.0
- Status: Stable and frozen
- Permitted stable changes: documented defects, security fixes and deployment fixes

## Active Recovery Branch
`docs/project-recovery-2026-07-15`

## Relevant Development Lines
- `maintenance/v1.0.1`: defect-maintenance line; 10 commits ahead and 2 behind main at recovery comparison; full regression not independently verified.
- `v1.1-development`: ERP Sprint 1 development line; 27 commits ahead and 2 behind main at recovery comparison; verified partial implementation.

## Verified Completed Scope
### Portfolio Edition v1.0.0
- Packaging Procurement
- Raw Material Procurement
- Category-aware should-cost and TCO
- Supplier risk and scoring
- Procurement Intelligence
- Supplier Intelligence and Supplier 360
- Supplier selector and per-profile code path
- SRM, financial, ESG, innovation and performance indicators
- Recommendation eligibility and business-rule validation
- Scenario stress testing and allocation
- Negotiation intelligence
- Executive memo, supplier email, narrative and explainability
- Business-readable and machine-readable exports
- Regression, adversarial, external-file and UI validation framework
- GitHub-first portability and handoff documentation

## Verified Partial Scope
### Version 1.1 ERP Foundation
- Canonical schema registry
- SAP, Oracle and custom mapping profiles
- Workbook loader
- Structural validator
- Synthetic and adversarial ERP workbook assets
- ERP data model, mapping and validation specifications
- Focused unit-test files

These items exist in code or test assets but are not accepted as Sprint 1 complete until the full suite and acceptance checklist are reconciled.

## Current Defects and Risks
1. **INR display/calculation consistency**
   - Main: reported defect remains outside the stable baseline.
   - Maintenance branch: corrective implementation and focused tests exist through PRs #5–#7.
   - Status: IMPLEMENTED BUT UNTESTED at recovery level.
2. **Supplier selector**
   - Main code contains a Supplier 360 `st.selectbox` and matching profile selection.
   - Status: VERIFIED COMPLETE in code; current live runtime still requires smoke validation.
3. **Branch divergence**
   - Maintenance and v1.1 lines branch from the v1.0.0 acceptance commit and are behind later portability documentation on main.
4. **Version 1.1 status inconsistency**
   - Main documentation says v1.1 is future-only, while a partial implementation branch exists.
5. **Unsupported test claim**
   - The reported `147 passed, 0 failed, 1 warning` result was not found in repository evidence.

## Latest Verified Test Result
- Historical v1.0.0 records document green CI, full regression, Streamlit smoke testing and manual acceptance.
- Current recovery did not independently execute the complete suite.
- GitHub combined status for main SHA returned no status records through the connector.
- PRs #5–#7 state that focused tests were added but not executed by the GitHub plugin.

## Deployment Status
- Streamlit deployment architecture and historical smoke acceptance are documented.
- Current hosted runtime health and deployment URL were not independently verified during recovery.
- Classification: IMPLEMENTED BUT UNTESTED for current-state recovery purposes.

## Pending Work
1. Capture exact current HEAD SHAs for maintenance and v1.1 branches.
2. Run and record the full test suite on main and maintenance.
3. Run Streamlit smoke and hosted-runtime checks.
4. Validate USD, INR and Both modes end to end.
5. Validate supplier selector against every supplier profile.
6. Reconcile portability controls into the approved maintenance baseline.
7. Reconstruct or rebase v1.1 from the approved maintenance baseline.
8. Reconcile the Sprint 1 checklist with actual code and test evidence.
9. Separately authorize any missing ERP upload pipeline, report or UI work.

## Deferred Work
- Time-aware procurement analytics
- Production ERP integration and write-back
- Live supplier-master, market-data, treasury, contract or workflow integrations
- External AI-provider integration without explicit security and architecture approval
- Autonomous supplier-award decisions

## Next Milestone
**Recovery Build R1 — Verify and close the v1.0.1 maintenance baseline.**

No feature implementation is authorized until exact branch baselines, full regression and deployment evidence are recorded.