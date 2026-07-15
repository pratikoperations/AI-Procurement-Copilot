# Project Recovery Manifest

## Repository Identity
- Repository: `pratikoperations/AI-Procurement-Copilot`
- Canonical source of truth: GitHub
- Canonical stable branch: `main`
- Verified stable baseline SHA: `39bfc2d0c75e58c883fdcec797f66dff2edd9eec`
- Documented release: Portfolio Edition v1.0.0
- Documented release status: Stable and frozen
- Recovery date: 2026-07-15

## Approved Classification Taxonomy
Every formal status must use exactly one of:
- VERIFIED COMPLETE
- VERIFIED PARTIAL
- IMPLEMENTED BUT UNTESTED
- DOCUMENTED ONLY
- REPORTED BUT NOT FOUND
- NOT STARTED
- DEFECT / REGRESSION
- DEFERRED
- OUT OF SCOPE

Runtime-validation requirements and unresolved evidence are recorded separately from the classification.

## Verified Development Lines
| Branch / line | Relationship to main | Verified purpose | Recovery classification |
|---|---:|---|---|
| `main` | Canonical stable line | Portfolio Edition v1.0.0 plus portability documentation | VERIFIED COMPLETE |
| `maintenance/v1.0.1` | 10 commits ahead, 2 behind; merge base `d4faca6ab86376ecd7a39587a1e443ece3f943b9` | Documented defect maintenance, including currency-display corrections | IMPLEMENTED BUT UNTESTED |
| `v1.1-development` | 27 commits ahead, 2 behind; merge base `d4faca6ab86376ecd7a39587a1e443ece3f943b9` | ERP upload Sprint 1 foundation | VERIFIED PARTIAL |
| `docs/project-recovery-2026-07-15` | Created from stable main SHA | Documentation-only recovery controls | VERIFIED PARTIAL |

Branch-search tooling did not return reliable direct HEAD listings. The branch relationships above are verified through GitHub compare evidence. Exact current HEAD SHAs for `maintenance/v1.0.1` and `v1.1-development` remain unresolved and must be recorded before any implementation or merge. PR merge SHAs and merge-base SHAs must not be substituted for current branch HEADs.

## Stable / Frozen Boundaries
- `main` and Portfolio Edition v1.0.0 must not receive new functionality.
- Permitted stable-line changes: documented defects, security fixes and deployment fixes only.
- Feature work must remain on a separate development branch.
- No undocumented work may be promoted based solely on conversation claims.

## Authoritative Documents
1. `PROJECT_RECOVERY_MANIFEST.md`
2. `PROJECT_STATUS.md`
3. `PROJECT_BUILD_PLAN.md`
4. `PENDING_WORK_REGISTER.md`
5. `PROJECT_ARCHITECTURE.md`
6. `BUSINESS_RULES.md`
7. `DATA_DICTIONARY.md`
8. `VERSION_MANIFEST.md`
9. `BUILD_HISTORY.md`
10. Validation records and executable tests

## Evidence-Based Recovery Findings
### Version 1.0.0
- Stable release documentation exists on `main`.
- The stable scope includes packaging and raw-material procurement, should-cost, TCO, risk, Supplier Intelligence, Supplier 360, scenarios, negotiation, executive outputs and exports.
- Main contains a supplier-selector capability in `modules/supplier_intelligence_ui.py` using `st.selectbox("Select Supplier 360 Profile", ...)`.
- Classification of the supplier-selector capability: VERIFIED COMPLETE.
- Main documentation records green CI, full regression, Streamlit smoke testing and manual acceptance for the release.
- Classification of the historical test and deployment acceptance records: DOCUMENTED ONLY.
- Current recovery did not independently rerun those tests or verify the hosted runtime.

### Version 1.0.1 Maintenance
- `maintenance/v1.0.1` exists and contains defect-fix work not present on current `main`.
- Merged PRs #5, #6 and #7 address Supplier Intelligence currency presentation and mobile visibility.
- PR records explicitly state that plugin-side tests were not executed.
- Classification of the INR issue on `main`: DEFECT / REGRESSION.
- Classification of the corrective maintenance implementation: IMPLEMENTED BUT UNTESTED.

### Version 1.1
- `v1.1-development` exists.
- Compared with `main`, it contains ERP mapping profiles, schema registry, workbook loader, structural validator, ERP sample workbooks, specifications and focused unit tests.
- No evidence was found in the compare set for a complete upload pipeline, validation-report generator or Streamlit upload UI.
- `planning/SPRINT1_TASK_CHECKLIST.md` remains entirely unchecked.
- The reported result `147 passed, 0 failed, 1 warning` was not found in repository evidence during recovery.

## Claim Classification
| Claim or capability | Classification | Evidence-based conclusion |
|---|---|---|
| Portfolio Edition v1.0.0 stable | VERIFIED COMPLETE | Documented on main with release controls |
| v1.0.0 frozen | VERIFIED COMPLETE | Explicit governance in `PROJECT_STATUS.md` |
| Supplier-level selector is missing | REPORTED BUT NOT FOUND | Selector exists on main |
| Supplier-selector capability on main | VERIFIED COMPLETE | Selector and matching profile-selection path exist |
| INR inconsistency on main | DEFECT / REGRESSION | Maintenance PRs show corrective work was required |
| INR corrective implementation on maintenance | IMPLEMENTED BUT UNTESTED | Code and focused tests exist; full regression and live validation remain pending |
| `v1.1-development` exists | VERIFIED COMPLETE | GitHub compare resolves the branch |
| Sprint 1 batches 1-6 complete | REPORTED BUT NOT FOUND | No authoritative completion record; checklist is unchecked |
| ERP schema registry | VERIFIED PARTIAL | Module and tests exist on v1.1 branch |
| ERP mapping profiles | VERIFIED PARTIAL | Profiles, module and tests exist |
| ERP workbook loader | VERIFIED PARTIAL | Module and tests exist |
| ERP structural validator | VERIFIED PARTIAL | Module and tests exist |
| ERP upload pipeline | REPORTED BUT NOT FOUND | Not present in verified compare file set |
| ERP validation reporting | REPORTED BUT NOT FOUND | Not present in verified compare file set |
| ERP upload UI | REPORTED BUT NOT FOUND | Not present in verified compare file set |
| `147 passed, 0 failed, 1 warning` | REPORTED BUT NOT FOUND | No repository evidence located |
| Historical Streamlit architecture and smoke acceptance | DOCUMENTED ONLY | Stable documents record historical acceptance |
| Current hosted Streamlit deployment healthy | REPORTED BUT NOT FOUND | Current hosted URL and runtime health were not independently observed |

## Recovery Procedure
1. Verify repository identity and default branch.
2. Record exact HEAD SHA for `main`, maintenance and development branches.
3. Compare each non-main branch with `main` and its merge base.
4. Inspect PR, commit, tag, release and workflow evidence.
5. Read project-control and architecture documents.
6. Inspect code and tests for every claimed capability.
7. Run full pytest and Streamlit smoke tests on each candidate baseline.
8. Record results in `PROJECT_ACTIVITY_LOG.md`, `PROJECT_STATUS.md` and `PENDING_WORK_REGISTER.md`.
9. Obtain owner approval for the proposed next controlled build.
10. Modify code only after the baseline and authorized scope are confirmed.

## Unresolved Discrepancies
- Exact current HEAD SHAs of `maintenance/v1.0.1` and `v1.1-development` require explicit branch-ref capture.
- Full regression has not been independently rerun during this connector-based recovery.
- Current hosted Streamlit URL and live runtime state were not available as verifiable repository evidence.
- Maintenance branch diverges from main because portability documentation was added to main after the common release base.
- Version 1.1 branch contains real partial implementation while main documentation still describes all v1.1 work as future planning.

## Recovery Decision
The correct development baseline is not yet approved for feature work. Preserve `main`; propose validation and reconciliation of `maintenance/v1.0.1`; obtain owner approval; then rebase or reconstruct `v1.1-development` from the approved v1.0.1 baseline before continuing ERP upload implementation.