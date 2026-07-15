# Recovery R1 Baseline Verification

Date: 2026-07-15

## Exact branch baselines
- Canonical main start: `075fe16d889cdb82b126fe1e07b0c63dca369580`
- `maintenance/v1.0.1` HEAD: `ba49af44d8c1ff36d9d5d612e0909f5698d1d433`
- `v1.1-development` HEAD: `0c2281e47ff4e2b4b8153fbde6350d5c9c1a4341`
- Recovery branch: `recovery/r1-v1.0.1-baseline-verification`

These are direct branch-ref resolutions, not PR merge SHAs, synthetic merge commits or merge-base SHAs.

## Reconciliation
The maintenance line diverged from current main. The 14 maintenance code/test files were reconstructed on current main to preserve recovery-governance and portability documentation.

## Scope
No Version 1.1 files, ERP work, formula redesign, schema expansion, award-control change or unrelated refactor was introduced.

Classification: VERIFIED COMPLETE for baseline capture; VERIFIED PARTIAL for release acceptance pending hosted and interactive validation.
