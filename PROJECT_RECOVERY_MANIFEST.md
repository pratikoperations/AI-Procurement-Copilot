# Project Recovery Manifest

## Repository Identity
- Repository: `pratikoperations/AI-Procurement-Copilot`
- Canonical source of truth: GitHub
- Canonical stable branch: `main`
- Recovery-governance baseline: `075fe16d889cdb82b126fe1e07b0c63dca369580`
- Recovery R1 merge SHA: `18c009fd2947cf66dba564f0d063c726ffc45319`
- Current main SHA: `ae50bca09e5cb33ed58439c6aecfcde4f391a846`
- Target release: Portfolio Edition v1.0.1
- Previous release: Portfolio Edition v1.0.0, preserved

## Approved Classification Taxonomy
Every formal status uses exactly one of: VERIFIED COMPLETE, VERIFIED PARTIAL, IMPLEMENTED BUT UNTESTED, DOCUMENTED ONLY, REPORTED BUT NOT FOUND, NOT STARTED, DEFECT / REGRESSION, DEFERRED, OUT OF SCOPE.

## Exact Branch Baselines
| Branch / baseline | Exact SHA / basis | Classification |
|---|---|---|
| `main` before Recovery R1 | `075fe16d889cdb82b126fe1e07b0c63dca369580` | VERIFIED COMPLETE |
| `maintenance/v1.0.1` | `ba49af44d8c1ff36d9d5d612e0909f5698d1d433` | VERIFIED COMPLETE |
| `v1.1-development` | `0c2281e47ff4e2b4b8153fbde6350d5c9c1a4341` | VERIFIED PARTIAL |
| Recovery R1 merged `main` | `18c009fd2947cf66dba564f0d063c726ffc45319` | VERIFIED COMPLETE |
| Display-version corrected `main` | `ae50bca09e5cb33ed58439c6aecfcde4f391a846` | VERIFIED COMPLETE |
| Reconciled PR #10 head | final SHA recorded in PR metadata | VERIFIED COMPLETE pending owner merge |

## Unexpected Main Commit Audit
Commit `ae50bca09e5cb33ed58439c6aecfcde4f391a846` changes only `README.md`, `VERSION_MANIFEST.md`, `app.py`, `modules/config.py`, and `tests/test_release_version.py`. It corrects displayed v1.0.1 metadata and adds three regression tests. It does not change procurement formulas, schemas, rankings, thresholds, approval controls, Version 1.1 or ERP functionality.

## Reconciliation Result
- Eight release-closure Markdown documents were reconstructed from current main.
- `app.py`, `modules/config.py` and `tests/test_release_version.py` remain exactly as accepted on current main and are absent from PR #10's diff.
- Owner-observed primary-main hosted acceptance is preserved.
- Final reconciled Quality Checks run 411: dependency install PASS; compile PASS; 165 passed, 0 failed, 0 skipped, 1 warning; Streamlit smoke PASS.

## Release Closure
| Item | Classification |
|---|---|
| Unexpected-main scoped audit | VERIFIED COMPLETE |
| Accepted version-display files preserved | VERIFIED COMPLETE |
| Eight-document PR boundary | VERIFIED COMPLETE |
| Final reconciled Quality Checks | VERIFIED COMPLETE |
| Primary-main hosted acceptance | VERIFIED COMPLETE |
| PR #10 merge | NOT STARTED |
| Annotated tag `v1.0.1` | NOT STARTED |
| GitHub release `Portfolio Edition v1.0.1` | NOT STARTED |
| Version 1.1 implementation | OUT OF SCOPE |

## Evidence Records
- `RECOVERY_R1_BASELINE_VERIFICATION.md`
- `RECOVERY_R1_MAIN_TEST_EVIDENCE.md`
- `RECOVERY_R1_MAINTENANCE_TEST_EVIDENCE.md`
- `RECOVERY_R1_CURRENCY_VALIDATION_MATRIX.md`
- `RECOVERY_R1_SUPPLIER_SELECTOR_VALIDATION.md`
- `RECOVERY_R1_DEPLOYMENT_EVIDENCE.md`
- `RECOVERY_R1_MAINTENANCE_RECONCILIATION_PLAN.md`

## Release Handoff Decision
PR #10 is ready for renewed owner approval and merge. The tag and GitHub release remain blocked until the resulting final main SHA is captured.
