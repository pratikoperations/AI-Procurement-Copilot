# Decision Log

## Preserved Governance Decisions
- GitHub is the canonical source of truth.
- Portfolio Edition v1.0.0 remains preserved and frozen.
- Award logic remains deterministic, auditable and human-controlled.
- Version 1.1 is real but partial; ERP feature work remains separately governed.
- Supplier-selector capability is VERIFIED COMPLETE.
- Historical deployment evidence remains distinct from current validation evidence.

## DEC-R1-001 — Exact Branch Baselines
- Main before Recovery R1: `075fe16d889cdb82b126fe1e07b0c63dca369580`
- Maintenance: `ba49af44d8c1ff36d9d5d612e0909f5698d1d433`
- v1.1: `0c2281e47ff4e2b4b8153fbde6350d5c9c1a4341`
- Classification: VERIFIED COMPLETE for baseline capture.

## DEC-R1-002 — Reconstruct Rather Than Rebase
- Decision: Reconstruct the verified maintenance files from canonical main.
- Basis: Historical maintenance history diverged and omitted later governance records.

## DEC-R1-003 — Correct Canonical Risk-TCO Source Preservation
- Decision: Preserve `Risk-Adjusted TCO (USD)` before rebuilding selected-currency outputs.
- Scope boundary: No FX formula, ranking, threshold, schema, recommendation or award-control change.
- Classification: VERIFIED COMPLETE.

## DEC-R1-004 — Executable Candidate Evidence
- Result: compile PASS; 162 passed, 0 failed, 0 skipped, 1 warning; Streamlit smoke PASS.
- Classification: VERIFIED COMPLETE.

## DEC-R1-005 — Standalone Main Baseline Evidence
- Result: compile PASS; 114 passed, 0 failed, 0 skipped, 1 warning; Streamlit smoke PASS.
- Classification: VERIFIED COMPLETE.

## DEC-R1-006 — Hosted Acceptance
- Recovery candidate and primary `main` were manually accepted by the project owner for startup, USD, INR, Both and all six Supplier 360 profiles.
- Classification: VERIFIED COMPLETE.

## DEC-R1-007 — Recovery R1 Promotion and Merge
- PR #9 merged to main as `18c009fd2947cf66dba564f0d063c726ffc45319`.
- Classification: VERIFIED COMPLETE.

## DEC-R1-008 — Unexpected Display-Version Commit Audit
- Commit: `ae50bca09e5cb33ed58439c6aecfcde4f391a846`.
- Files: `README.md`, `VERSION_MANIFEST.md`, `app.py`, `modules/config.py`, `tests/test_release_version.py`.
- Decision: accept and preserve the v1.0.1 edition/build/docstring correction and its dedicated regression coverage.
- Scope finding: no procurement formula, schema, ranking, threshold, approval-control, Version 1.1 or ERP change.
- Classification: VERIFIED COMPLETE for scoped audit.

## DEC-R1-009 — Reconstruct Release Closure from Current Main
- Decision: do not rebase the conflicted 17-commit closure history.
- Reconstruct the eight approved Markdown documents on `release/v1.0.1-closure-reconciled` from current main `ae50bca09e5cb33ed58439c6aecfcde4f391a846`.
- Preserve `app.py`, `modules/config.py` and `tests/test_release_version.py` exactly as already accepted on current main.
- Replace PR #10 head only after reconstruction is complete.
- Classification: DOCUMENTED ONLY pending final diff and CI verification.

## DEC-R1-010 — Tag and Release Gate
- PR #10 must remain draft and unmerged until the reconciled head contains exactly eight Markdown files and final Quality Checks pass.
- Annotated tag `v1.0.1` must target the final approved release-closure main SHA.
- Existing v1.0.0 tag and release must not be modified.
- Tag status: NOT STARTED.
- GitHub release status: NOT STARTED.

## Version 1.1 Boundary
Version 1.1 implementation remains OUT OF SCOPE until separately authorized after v1.0.1 release closure.
