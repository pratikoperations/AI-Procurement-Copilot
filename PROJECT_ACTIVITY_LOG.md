# Project Activity Log

## Historical Baselines
- 2026-07-11 — `d4faca6ab86376ecd7a39587a1e443ece3f943b9`: v1.0.0 manual validation acceptance recorded.
- 2026-07-13 — `39bfc2d0c75e58c883fdcec797f66dff2edd9eec`: portability maintenance backlog added.
- 2026-07-15 — PR #8 merged as `075fe16d889cdb82b126fe1e07b0c63dca369580`, establishing recovery governance.

## Recovery Build R1 Activity
| Date | Commit / PR / run | Activity | Tests / evidence | Result | Remaining action |
|---|---|---|---|---|---|
| 2026-07-15 | branch-ref capture | Resolved exact maintenance and v1.1 HEADs | Direct branch resolution | `ba49af44...`; `0c2281e4...` | Preserve in evidence |
| 2026-07-15 | `9f337239cc120433c5cc2cd98274d890ad12f113` | Reconstructed 14 maintenance files on canonical main | Initial canonical CI | Compile PASS; regression FAIL; smoke skipped | Isolate failure |
| 2026-07-15 | diagnostic run 361 | Ran focused maintenance files separately | GitHub Actions | Supplier Intelligence currency test failed; others passed | Inspect source handling |
| 2026-07-15 | `acda17383cb1bed09787f69345ea60e359b94b06` | Preserved canonical risk-TCO source during display rebuild | Focused tests, full suite, smoke | All PASS | Capture exact counts |
| 2026-07-15 | run 363 | Captured candidate environment and artifact | Python 3.11.15 | 162 passed, 0 failed, 0 skipped, 1 warning; smoke PASS | Restore workflow |
| 2026-07-15 | `5d004cae63a1eb21c03fe4acba2a8cf0670aa54b` | Restored canonical workflow | File content restored | No net workflow change | Confirm final diff |
| 2026-07-15 | run 376 | Final canonical candidate CI | Install, compile, pytest, smoke | PASS | Acceptance closure |
| 2026-07-15 | run 377 | Independently checked out exact main SHA `075fe16d...` | Python 3.11.15, pinned dependencies, compile, pytest, smoke | 114 passed, 0 failed, 0 skipped, 1 warning; smoke PASS | Restore workflow |
| 2026-07-15 | `81b09c3efcdb2a4f50b182df8beb241cbbefd593` | Restored canonical workflow after standalone-main run | Workflow blob restored | No workflow diff intended | Final diff/CI check |
| 2026-07-15 | PR #9 | Updated seven evidence records and mandatory project memory | Documentation review | Hosted URL still not found; interactive acceptance not started | Keep draft and unmerged |

## Controlled Decision
Reconstruction from current main remains preferred over rebasing the divergent maintenance branch. Promotion verdict remains **CHANGES REQUIRED** because hosted deployment, supplier-by-supplier interaction and hosted currency-mode acceptance are not directly evidenced.

## Mandatory Future Log Rule
Every substantive build must record exact branch/commit, files, commands, results, decision and remaining action, and update the mandatory project-memory files.
