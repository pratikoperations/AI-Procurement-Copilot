# Project Activity Log

## Historical Baselines
- 2026-07-11 — `d4faca6ab86376ecd7a39587a1e443ece3f943b9`: v1.0.0 manual validation acceptance recorded.
- 2026-07-13 — `39bfc2d0c75e58c883fdcec797f66dff2edd9eec`: portability maintenance backlog added.
- 2026-07-15 — PR #8 merged as `075fe16d889cdb82b126fe1e07b0c63dca369580`, establishing recovery governance.

## Recovery Build R1 Activity
| Date | Commit / PR / run | Activity | Tests / evidence | Result | Remaining action |
|---|---|---|---|---|---|
| 2026-07-15 | branch-ref capture | Resolved exact maintenance and v1.1 HEADs | Direct branch resolution | `ba49af44...`; `0c2281e4...` | Preserve in evidence |
| 2026-07-15 | `9f337239...` | Reconstructed 14 maintenance files on canonical main | Initial canonical CI | Compile PASS; regression FAIL | Isolate failure |
| 2026-07-15 | `acda1738...` | Preserved canonical risk-TCO source during display rebuild | Focused tests, full suite, smoke | All PASS | Capture exact counts |
| 2026-07-15 | run 377 | Independently checked exact pre-maintenance main | Python 3.11.15, compile, pytest, smoke | 114 passed, 0 failed, 0 skipped, 1 warning; smoke PASS | Retain evidence |
| 2026-07-15 | PR #9 / `18c009fd...` | Merged validated maintenance to main | 162-test candidate and hosted acceptance | Recovery R1 merged | Release closure |

## v1.0.1 Release Closure
| Date | Branch / PR / run | Activity | Scope / evidence | Result | Remaining action |
|---|---|---|---|---|---|
| 2026-07-15 | `release/v1.0.1-closure` / PR #10 | Opened documentation closure | Eight Markdown files | Initial closure checks PASS | Owner acceptance |
| 2026-07-15 | primary main deployment | Owner verified main after PR #9 | Startup, USD/INR/Both, six supplier profiles | All accepted | Final closure |
| 2026-07-15 | `ae50bca0...` | Unexpected direct main commit corrected displayed v1.0.1 metadata and added regression test | README, VERSION_MANIFEST, app docstring, config metadata, one test | Narrow version-display change; no procurement logic or v1.1/ERP scope | Reconcile PR #10 |
| 2026-07-15 | `release/v1.0.1-closure-reconciled` | Reconstructed closure documents from current main | Preserve current-main app/config/test changes and eight-document governance scope | Reconstruction in progress | Final CI and review |

## Controlled Decision
Reconstruction from current main is the safest reconciliation method. PR #10 must remain draft and unmerged until its head is replaced by the reconciled branch, the final diff contains only the eight approved Markdown files, and final Quality Checks pass.

## Mandatory Future Log Rule
Every substantive build must record exact branch/commit, files, commands, results, decision and remaining action, and update the mandatory project-memory files.
