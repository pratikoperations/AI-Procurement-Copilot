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
- `maintenance/v1.0.1`: defect-maintenance line; 10 commits ahead and 2 behind main at recovery comparison; classification: IMPLEMENTED BUT UNTESTED.
- `v1.1-development`: ERP Sprint 1 development line; 27 commits ahead and 2 behind main at recovery comparison; classification: VERIFIED PARTIAL.

Exact current HEAD SHAs for both non-main lines remain unresolved and must not be inferred from merge SHAs or merge-base SHAs.

## Verified Completed Scope
### Portfolio Edition v1.0.0
Classification: VERIFIED COMPLETE

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
Classification: VERIFIED PARTIAL

- Canonical schema registry
- SAP, Oracle and custom mapping profiles
- Workbook loader
- Structural validator
- Synthetic and adversarial ERP workbook assets
- ERP data model, mapping and validation specifications
- Focused unit-test files

These items exist in code or test assets but are not accepted as Sprint 1 complete until the full suite and acceptance checklist are reconciled.

## Current Defects, Claims and Risks
1. **INR display/calculation consistency on main**
   - Classification: DEFECT / REGRESSION.
   - Maintenance PRs #5–#7 show that corrective work was required.
2. **INR corrective implementation on maintenance/v1.0.1**
   - Classification: IMPLEMENTED BUT UNTESTED.
   - Corrective code and focused tests exist; full regression and live validation remain pending.
3. **Claim that Supplier Intelligence lacks a supplier selector**
   - Classification: REPORTED BUT NOT FOUND.
   - Main code already contains the selector and matching profile-selection path.
4. **Supplier-selector capability on main**
   - Classification: VERIFIED COMPLETE.
   - Runtime validation across every supplier remains a pending validation action, not a second classification.
5. **Branch divergence**
   - Maintenance and v1.1 lines branch from the v1.0.0 acceptance commit and are behind later portability documentation on main.
6. **Version 1.1 status inconsistency**
   - Main documentation says v1.1 is future-only, while a partial implementation branch exists.
7. **Unsupported test claim**
   - The reported `147 passed, 0 failed, 1 warning` result is classified REPORTED BUT NOT FOUND.

## Test Status
- Historical v1.0.0 green CI, full regression, Streamlit smoke testing and manual acceptance: DOCUMENTED ONLY.
- Current complete-suite execution during recovery: NOT STARTED.
- PRs #5–#7 contain focused tests, but recovery-level execution remains pending.

## Deployment Status
- Historical Streamlit deployment architecture and smoke acceptance: DOCUMENTED ONLY.
- Current hosted Streamlit deployment-health claim: REPORTED BUT NOT FOUND.
- Current hosted URL and runtime health were not independently observed during recovery.

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

Classification: DEFERRED.

## Proposed Next Controlled Build — Pending Owner Approval
**Recovery Build R1 — Verify and close the v1.0.1 maintenance baseline.**

No subsequent build is authorized until the owner explicitly approves it. No feature implementation may begin until exact branch baselines, full regression and deployment evidence are recorded.
