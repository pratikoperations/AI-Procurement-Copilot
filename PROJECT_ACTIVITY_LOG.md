# Project Activity Log

This log records evidence recovered from Git history and the 2026-07-15 forensic reconciliation. It does not convert undocumented claims into completed work.

## Historical and Recovered Activity
| Date | Branch | Commit / PR | Activity | Files changed | Tests performed | Result | Decision | Remaining action |
|---|---|---|---|---|---|---|---|---|
| 2026-07-11 | main | `d4faca6ab86376ecd7a39587a1e443ece3f943b9` | Finalized v1.0.0 manual validation acceptance | Release and validation records | Historical full regression, Streamlit and manual acceptance documented | Portfolio Edition v1.0.0 accepted | Freeze release except approved maintenance | Preserve release baseline |
| 2026-07-13 | main | `761883a27abdea502c89f884c0329572cb2a9250` | Added portability and handoff foundation | Architecture, handoff, setup, deployment, troubleshooting and contribution docs | Documentation-only; existing suite retained as baseline | Knowledge portability improved | GitHub is canonical project memory | Keep controls current |
| 2026-07-13 | main | `39bfc2d0c75e58c883fdcec797f66dff2edd9eec` | Added optional portability maintenance backlog | Documentation | No independent rerun recorded in recovery | Current verified main HEAD | Use as recovery branch base | Do not add features to main |
| 2026-07-15 | maintenance/v1.0.1 | PR #5 | Added selected-currency handling in Supplier Intelligence | UI/currency modules and focused tests | Tests added; GitHub plugin did not execute them | Merged to maintenance branch | Classification: IMPLEMENTED BUT UNTESTED | Run full regression and smoke test |
| 2026-07-15 | maintenance/v1.0.1 | PR #6 | Corrected quoted-price display derivation from canonical normalized value | Supplier Intelligence currency code and tests | Tests added; GitHub plugin did not execute them | Merged to maintenance branch | Preserve audit metadata and canonical calculation basis | Run focused and full tests |
| 2026-07-15 | maintenance/v1.0.1 | PR #7 | Prioritized selected-currency columns for mobile visibility | Supplier Intelligence currency UI and tests | Tests added; GitHub plugin did not execute them | Merged to maintenance branch | Classification: IMPLEMENTED BUT UNTESTED | Verify live USD/INR/Both behavior |
| Date not established | v1.1-development | 27 commits ahead of common release base | Added ERP Sprint 1 foundation | Schema registry, mapping profiles, workbook loader, structural validator, samples, specifications and tests | Focused test files exist; authoritative run result not found | Classification: VERIFIED PARTIAL | Do not call Sprint 1 complete | Capture branch HEAD; run suite; reconcile checklist |

## Recovery-Control Branch — Original Eight Commits
| Date | Branch | Commit | Activity | File changed | Tests performed | Result |
|---|---|---|---|---|---|---|
| 2026-07-15 | docs/project-recovery-2026-07-15 | `62516296a24df34b8c8f1deaa75c32b800a5b0be` | Established recovery manifest | `PROJECT_RECOVERY_MANIFEST.md` | No runtime tests required or executed; Markdown governance only | Recovery controls initiated |
| 2026-07-15 | docs/project-recovery-2026-07-15 | `a839ec1ef39e0902de7145483519805d79fac9bd` | Reconciled build plan | `PROJECT_BUILD_PLAN.md` | No runtime tests required or executed; Markdown governance only | Controlled roadmap established |
| 2026-07-15 | docs/project-recovery-2026-07-15 | `48cbaa230072149d8cd1cbfdfe417cd314ffa94d` | Added activity log | `PROJECT_ACTIVITY_LOG.md` | No runtime tests required or executed; Markdown governance only | Historical recovery evidence recorded |
| 2026-07-15 | docs/project-recovery-2026-07-15 | `73b6a9db5fa07ad496ec806639e9780c398a092a` | Added pending-work register | `PENDING_WORK_REGISTER.md` | No runtime tests required or executed; Markdown governance only | Pending work governed |
| 2026-07-15 | docs/project-recovery-2026-07-15 | `a63fb5b0cab7e9f7381b7967f80e54541acfb56b` | Reconciled decision log | `DECISION_LOG.md` | No runtime tests required or executed; Markdown governance only | Recovery decisions recorded |
| 2026-07-15 | docs/project-recovery-2026-07-15 | `d9dc82e65d450cc0ba20bec746f83dd47b1b699c` | Reconciled project status | `PROJECT_STATUS.md` | No runtime tests required or executed; Markdown governance only | Verified and disputed scope separated |
| 2026-07-15 | docs/project-recovery-2026-07-15 | `98b96c3b5a0ca189cc45db3e5380ecbafe2505a6` | Reconciled architecture | `PROJECT_ARCHITECTURE.md` | No runtime tests required or executed; Markdown governance only | Stable and partial ERP architecture separated |
| 2026-07-15 | docs/project-recovery-2026-07-15 | `aa5da845f7872dfc52032fdff04461f85f403e1b` | Updated mandatory AI handoff sequence | `AI_HANDOFF_GUIDE.md` | No runtime tests required or executed; Markdown governance only | Initial recovery-control document set completed |

## Pull Request and Review Activity
| Date | Branch / PR | Commit / PR | Activity | Files changed | Tests performed | Result | Decision | Remaining action |
|---|---|---|---|---|---|---|---|---|
| 2026-07-15 | PR #8 | Draft PR #8 | Opened recovery-governance pull request against `main` | Eight Markdown governance files | No runtime tests required or executed; documentation-only scope | Draft opened; main unchanged | Do not merge before review | Complete governance review |
| 2026-07-15 | PR #8 | Review at `aa5da845f7872dfc52032fdff04461f85f403e1b` | Reviewed documentation boundary, classifications, activity completeness and approval wording | Eight Markdown governance files | No runtime tests required or executed; no code, schema, dependency, test, workflow, configuration, dataset or deployment files changed | CHANGES REQUIRED BEFORE MERGE | Apply taxonomy, activity-log and approval-language corrections | Re-review corrected head |

## Governance-Correction Commits
| Date | Branch | Commit | Activity | Files changed | Tests performed | Result |
|---|---|---|---|---|---|---|
| 2026-07-15 | docs/project-recovery-2026-07-15 | `6b39b95f6e12630318a656fe7b0b0357f74cd078` | Corrected recovery classifications | `PROJECT_RECOVERY_MANIFEST.md` | No runtime tests required or executed; Markdown governance only | Claim/capability and deployment classifications separated |
| 2026-07-15 | docs/project-recovery-2026-07-15 | `11b7dd1b832e13f0b9226520a40e06fe518203e0` | Corrected project-status taxonomy | `PROJECT_STATUS.md` | No runtime tests required or executed; Markdown governance only | INR, selector and deployment statuses standardized |
| 2026-07-15 | docs/project-recovery-2026-07-15 | `08fdee63a7d6722c8458f09b01d4c26ade99e567` | Corrected next-build approval wording | `PROJECT_BUILD_PLAN.md` | No runtime tests required or executed; Markdown governance only | Next controlled build marked pending owner approval |
| 2026-07-15 | docs/project-recovery-2026-07-15 | `e1c86042c4ee081da29e19164aebba2d7288eaa5` | Corrected decision governance | `DECISION_LOG.md` | No runtime tests required or executed; Markdown governance only | DEC-014 changed to proposal pending approval |
| 2026-07-15 | docs/project-recovery-2026-07-15 | `a9f6af1a47da0aa241b01c7e146efb6fbde2afe1` | Standardized pending-work classifications | `PENDING_WORK_REGISTER.md` | No runtime tests required or executed; Markdown governance only | Every formal status now uses one approved classification |

## Branch Head Recording Rule
- Reviewed baseline before corrections: `aa5da845f7872dfc52032fdff04461f85f403e1b`.
- Recovery-control content HEAD immediately before this activity-log closure commit: `a9f6af1a47da0aa241b01c7e146efb6fbde2afe1`.
- The final PR head after this file is committed is authoritative in PR metadata and in the post-edit recovery report. A commit cannot contain its own final SHA because the file content contributes to that SHA; therefore the immediately preceding content HEAD and the externally verified final PR head are both recorded.

## Mandatory Future Log Rule
Every substantive build must append entries showing branch, exact commit/PR, files, test commands and results, decision and remaining action. A build is not complete until this log, `PROJECT_STATUS.md`, `PENDING_WORK_REGISTER.md` and `PROJECT_RECOVERY_MANIFEST.md` are updated.