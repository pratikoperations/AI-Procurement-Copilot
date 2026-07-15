# Recovery R1 Maintenance Reconciliation Plan

Date: 2026-07-15

## Selected Approach
**Reconstruct the validated v1.0.1 corrections on a new branch from current canonical main.**

The historical maintenance line diverged from current main and omitted later portability and recovery-governance records. Reconstruction preserves canonical controls while limiting application/test changes to approved maintenance scope.

## Verified Result
- Exact main start: `075fe16d889cdb82b126fe1e07b0c63dca369580`
- Exact maintenance HEAD: `ba49af44d8c1ff36d9d5d612e0909f5698d1d433`
- Exact v1.1 HEAD: `0c2281e47ff4e2b4b8153fbde6350d5c9c1a4341`
- Fourteen maintenance files reconstructed.
- One source-preservation defect corrected in `modules/supplier_intelligence_currency_ui.py`.
- Standalone main: compile PASS; 114 passed, 0 failed, 0 skipped, 1 warning; smoke PASS.
- Candidate: compile PASS; 162 passed, 0 failed, 0 skipped, 1 warning; smoke PASS.
- Hosted candidate: startup PASS; all six supplier profiles and USD/INR/Both modes accepted by the project owner.
- Final PR contains no workflow-file change and no Version 1.1/ERP feature file.

## Promotion Recommendation
**MERGE READY**

All Recovery R1 acceptance gates are closed. Hosted acceptance is based on owner-observed manual validation at `https://ai-procurement-copilot-pr9.streamlit.app/` and is recorded separately from automated CI evidence.

The PR must remain draft and unmerged until the owner performs the final review and explicitly authorizes merge.
