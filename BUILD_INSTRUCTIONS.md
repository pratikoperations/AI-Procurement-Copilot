# Build Instructions

## Purpose
This file explains how to resume and continue AI Procurement Copilot under the current stabilized, governed workflow if chat history is lost.

## Recovery Start Point
Always begin by reading these files in order:

1. `AGENTS.md`
2. `README.md`
3. `PROJECT_STATUS.md`
4. `VERSION_MANIFEST.md`
5. `CONTRIBUTING.md`
6. `PROJECT_RECOVERY_MANIFEST.md`
7. `PENDING_WORK_REGISTER.md`
8. current architecture, governance and test-evidence documents relevant to the task
9. `DECISION_LOG.md`, `BUILD_HISTORY.md` and `CHANGELOG.md` for historical context

Do not treat older recovery/release instructions as current merely because they remain in Git history.

## Build Rules
1. GitHub is the canonical source of truth.
2. Read and follow root `AGENTS.md` before editing.
3. Work from current `main` on a focused branch; do not push governed work directly to `main`.
4. Define acceptance criteria before editing.
5. Make the smallest coherent change and avoid unrelated formatting/refactoring.
6. Do not invent procurement formulas, FX rates, defaults, schemas, thresholds, rankings, eligibility logic or approval controls.
7. Add or update targeted tests when behaviour changes.
8. Run risk-appropriate validation and report exactly what was and was not executed.
9. Review the full diff for unrelated changes, secrets, sensitive data and governance drift.
10. Update project status/history/decision records only when the change materially requires it.
11. Every meaningful milestone must be preserved in Git/GitHub; no major work should exist only in chat.
12. Capture the exact PR head before final approval/merge. If the head changes, re-verify.
13. Do not force-push, rewrite history, move tags, create releases or deploy without explicit authorization.
14. The app should remain runnable after each completed implementation milestone unless the task explicitly concerns a documented non-runtime artifact.

## Current Operating Boundary
The project is under stabilization freeze. Routine feature expansion and cosmetic churn are closed.

The following boundaries must be preserved unless explicitly re-authorized through a separate architecture/governance decision:
- human procurement approval is mandatory;
- no autonomous supplier award, approval or qualification;
- no production allocation execution;
- no live ERP write-back;
- SourceMate remains read-only and deterministic, without external LLM, RAG, web-browsing or hidden recalculation authority;
- MRO / Industrial Supplies remains Foundation Preview unless a separately governed capability explicitly changes that status;
- public demonstration uses only synthetic or sanitized data;
- confidential supplier, contract, personal, credential or commercially sensitive data must not be introduced into the public demo or assistant workflow.

## Development Sequence

```text
Validate objective and scope
Read AGENTS.md + current control docs
Define acceptance criteria
Create focused branch
Inspect affected architecture/business rules
Implement smallest coherent change
Add/update tests as required
Run risk-appropriate checks
Review complete diff
Update required documentation/evidence
Open/update pull request
Verify exact head + CI/check evidence
Owner approval
Merge exact verified head
```

## Local Run Command

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Test Command

```bash
python -m pytest
```

Additional quality gates may include compile, Ruff, targeted mypy, dependency audit, Streamlit smoke and browser/mobile acceptance depending on the change.

## Current Canonical Baseline
- `main`: `d6d1e741205e6c0ceb37a8d3617e9aafd6d26e55`
- Latest governed extension: MRO-0 / PR #109
- Post-merge main Quality Checks: run 1138 / run ID `38204618690` — SUCCESS
- Project mode: stabilized portfolio/interview product under controlled freeze

## Current Controlled Build
**Final closure documentation reconciliation**

Purpose:
- remove stale PR #108 bootstrap instructions;
- record the post-MRO-0 current baseline and validation evidence;
- preserve the hosted-acceptance boundary;
- leave runtime/business behavior unchanged.

## Next Build
No feature build is pre-authorized. After this documentation reconciliation is merged, the project should remain frozen unless a separate business case authorizes a new task.

Manual hosted acceptance of the deployed post-MRO-0 application remains the next evidence gate; it is not a feature build and does not by itself authorize runtime changes.
