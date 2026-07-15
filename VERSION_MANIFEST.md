# Version Manifest

## Project
AI Procurement Copilot

## Release
Portfolio Edition v1.0.1

## Status
Release candidate — documentation closure pending owner approval, merge, tag and GitHub release

## Release Basis
- Recovery R1 merged maintenance baseline: `18c009fd2947cf66dba564f0d063c726ffc45319`
- Display-version correction on current main: `ae50bca09e5cb33ed58439c6aecfcde4f391a846`
- Historical stable foundation: Portfolio Edition v1.0.0
- Reconciled release-closure branch: `release/v1.0.1-closure-reconciled`

## Active Category Engines
- Packaging Procurement — Stable
- Raw Material Procurement — Stable

## v1.0.1 Maintenance Scope
- Governed USD, INR and Both display handling across supported business-facing surfaces.
- Supplier Intelligence risk-adjusted TCO source-preservation correction.
- Preservation of original and normalized quotation values, FX metadata, units and comparison basis.
- Preservation of supplier rankings, formulas, recommendation eligibility, thresholds and human approval controls.
- Mobile-priority business currency columns and governed readable exports.
- Displayed edition and build metadata corrected to v1.0.1 with regression coverage.

## Release Integrity
- Original and normalized quotation data remain separated.
- Currency and unit consistency remain governed.
- No double conversion is permitted.
- Canonical audit fields remain unchanged by display-mode selection.
- Supplier rankings and award-control behaviour remain unchanged.
- Human approval remains mandatory.
- No Version 1.1 or ERP feature implementation is included.

## Validation Status
- Standalone pre-maintenance main: 114 passed, 0 failed, 0 skipped, 1 warning; Streamlit smoke PASS.
- Reconstructed v1.0.1 candidate: 162 passed, 0 failed, 0 skipped, 1 warning; Streamlit smoke PASS.
- Final PR #9 Quality Checks: PASS.
- Recovery R1 hosted deployment startup: PASS.
- Six-supplier hosted acceptance: VERIFIED COMPLETE through owner-observed manual validation.
- Hosted USD, INR and Both acceptance: VERIFIED COMPLETE through owner-observed manual validation.
- Primary `main` deployment after PR #9: VERIFIED COMPLETE through owner-observed manual validation.
- Display-version metadata and regression coverage on current main: VERIFIED COMPLETE.
- Critical defects open for v1.0.1 scope: 0.
- Major defects open for v1.0.1 scope: 0.

## Release Governance
- v1.0.1 is frozen as the stable maintenance release after closure approval, merge, tagging and release publication.
- v1.0.0 remains the historical first stable portfolio release and must not be modified or retagged.
- v1.0.1 is maintenance-only and introduces no new feature scope.
- Tag `v1.0.1` must target the approved release-closure main SHA after the documentation PR is merged.
- Version 1.1 remains a separately governed development stream.

## Evidence
- `RECOVERY_R1_BASELINE_VERIFICATION.md`
- `RECOVERY_R1_MAIN_TEST_EVIDENCE.md`
- `RECOVERY_R1_MAINTENANCE_TEST_EVIDENCE.md`
- `RECOVERY_R1_CURRENCY_VALIDATION_MATRIX.md`
- `RECOVERY_R1_SUPPLIER_SELECTOR_VALIDATION.md`
- `RECOVERY_R1_DEPLOYMENT_EVIDENCE.md`
- `RECOVERY_R1_MAINTENANCE_RECONCILIATION_PLAN.md`

## Next Controlled Action
Run final Quality Checks on the reconciled documentation-only PR, merge after owner approval, capture final `main`, then create annotated tag `v1.0.1` and GitHub release `Portfolio Edition v1.0.1`.
