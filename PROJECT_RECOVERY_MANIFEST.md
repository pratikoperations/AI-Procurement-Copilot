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
| Display-version corrected `main` | `ae50bca09e5cb33ed58439c6aecfcde4f391a846` | VERIFIED COMPLETE for scoped audit |
| Reconciled closure branch | `release/v1.0.1-closure-reconciled` | DOCUMENTED ONLY pending final CI and merge |

## Recovery R1 Findings
- Fourteen approved maintenance code/test files were reconstructed on canonical main.
- A risk-adjusted TCO source-preservation defect was discovered and corrected.
- No FX formula, ranking, threshold, schema, recommendation or award-control rule changed.
- Standalone pre-maintenance main: 114 passed, 0 failed, 0 skipped, 1 warning; smoke PASS.
- v1.0.1 candidate: 162 passed, 0 failed, 0 skipped, 1 warning; smoke PASS.
- Hosted Recovery R1 and primary-main owner acceptance: VERIFIED COMPLETE.

## Unexpected Main Commit Audit
Commit `ae50bca09e5cb33ed58439c6aecfcde4f391a846` changes only:
- `README.md`
- `VERSION_MANIFEST.md`
- `app.py`
- `modules/config.py`
- `tests/test_release_version.py`

It corrects displayed v1.0.1 metadata and adds regression coverage. It does not change procurement formulas, schemas, rankings, thresholds, approval controls, Version 1.1 or ERP functionality.

## Release Reconciliation
| Item | Classification |
|---|---|
| Accepted app/config/version-test changes preserved on current main | VERIFIED COMPLETE |
| Owner-observed primary-main hosted acceptance preserved | VERIFIED COMPLETE |
| Eight-document release closure reconstructed from current main | DOCUMENTED ONLY |
| Final PR #10 file boundary | NOT STARTED pending ref replacement and verification |
| Final reconciled Quality Checks | NOT STARTED |
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
Reconstructing the closure documents from current main is preferred over rebasing the conflicted history. Do not merge, tag or publish the release until the reconciled PR contains exactly eight Markdown files and final Quality Checks pass.
