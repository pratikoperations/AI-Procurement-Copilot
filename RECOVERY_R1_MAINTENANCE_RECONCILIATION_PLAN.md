# Recovery R1 Maintenance Reconciliation Plan

Date: 2026-07-15

## Selected approach
**Reconstruct the validated v1.0.1 corrections on a new branch from current canonical main.**

## Why
The historical maintenance line diverged from current main and omitted later portability and recovery-governance records. Reconstruction preserves the canonical documentation while limiting code/test changes to the 14 maintenance files.

## Reconstruction result
- 14 maintenance files transplanted from exact maintenance HEAD.
- One source-preservation defect discovered and corrected in `modules/supplier_intelligence_currency_ui.py`.
- Final compile, 162-test regression and Streamlit smoke gates pass.
- No Version 1.1 files or unrelated feature work included.

## Promotion recommendation
**CHANGES REQUIRED** before merge because:
1. current hosted deployment URL/health is not independently verified;
2. every supplier option has not been manually exercised in the hosted UI;
3. final PR review must confirm the temporary diagnostic workflow commits net to no workflow diff.

Once those acceptance checks are completed and the final diff/CI remain clean, the candidate may be reconsidered as MERGE READY.
