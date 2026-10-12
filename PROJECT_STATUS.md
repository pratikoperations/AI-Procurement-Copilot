# Project Status

## Canonical Repository State
- Repository: `pratikoperations/AI-Procurement-Copilot`
- Canonical stable branch: `main`
- Current accepted `main` HEAD: `d6d1e741205e6c0ceb37a8d3617e9aafd6d26e55`
- Latest merged governed capability: MRO-0 / PR #109
- MRO-0 source head: `9a35873b8ae08a3fd7c5bc9747287ad4fe9880c0`
- Post-merge Quality Checks: run 1138 / run ID `38204618690` — SUCCESS
- Frozen v1.2 historical baseline: `4803b1d72fa8a6509d9d7faf0e9decc677c447be`
- Frozen v1.1 historical baseline: `b85cd37aaae709058eb15350d680b18c03da46ba`
- Hosted application: `https://ai-procurement-copilot.streamlit.app/`

## Current Operating Mode
**STABILIZATION FREEZE / PORTFOLIO-INTERVIEW PRODUCT**

The functional portfolio/interview build is complete at its currently approved scope. Routine feature expansion and cosmetic churn remain closed.

Separately authorized bounded work may include:
- verified defect correction;
- security or privacy hardening;
- material documentation reconciliation;
- hosted/interview-readiness correction;
- testing or governance improvements that do not silently change product behaviour.

Any new capability expansion requires a separate business case and explicit approval before implementation.

## Current Product Boundary
- Governed procurement decision support only.
- Human procurement approval remains mandatory.
- No autonomous supplier qualification, award or approval.
- No production allocation execution.
- No live ERP write-back.
- SourceMate remains read-only and deterministic; it does not browse the web, call an external LLM, use RAG, recalculate authoritative procurement results or execute procurement actions.
- MRO / Industrial Supplies remains **Foundation Preview** only.
- MRO-0 has no MRO should-cost, supplier scoring, scenario, negotiation or allocation execution.
- Approved Equivalent substitution requires explicit human approval.
- Synthetic or sanitized data only for public demonstration; confidential supplier, contract, personal, credential or commercially sensitive data must not be uploaded.

## Current Accepted Quality Evidence
For MRO-0 and the current main baseline:
- PR source head: `9a35873b8ae08a3fd7c5bc9747287ad4fe9880c0`
- PR Quality Checks run 1137 / run ID `38203428348` — SUCCESS
- PR Mobile Browser Acceptance run 153 / run ID `38203428355` — SUCCESS
- Resulting main SHA: `d6d1e741205e6c0ceb37a8d3617e9aafd6d26e55`
- Main Quality Checks run 1138 / run ID `38204618690` — SUCCESS

Hosted behavior is a separate evidence gate. CI success must not be represented as hosted acceptance.

## Governance State
- GitHub is the canonical source of truth.
- `main` is the stable branch.
- Focused branch + pull request workflow is required for meaningful changes.
- Exact-head verification is required before merge when the head can move.
- No direct push to `main` for governed work.
- No force push, history rewrite, tag creation, release creation or deployment without explicit authorization.
- Procurement formulas, schemas, thresholds, rankings, recommendation eligibility and approval controls must not be invented or changed implicitly.
- PR #1 must remain open, Draft and unmerged unless separately and explicitly governed.

## Completed Governance Bootstrap
PR #108 — Codex governance bootstrap and control-document reconciliation — is complete and merged. Its historical “next action” is no longer active.

## Completed MRO-0 Gate
PR #109 — MRO-0 — Add Industrial Supplies category foundation — is complete and merged.

MRO-0 establishes:
- Industrial Bearings as the first representative MRO commodity;
- manufacturer + manufacturer-part-number identity;
- OEM / Authorized Distributor / Approved Equivalent source status;
- technical, commercial, evidence and supplier-data contracts;
- fail-closed technical compatibility;
- explicit human approval for equivalent substitution and supplier selection;
- qualitative risk dimensions without invented numerical weights;
- synthetic demonstration evidence boundaries.

MRO analytical execution remains intentionally disabled.

## Documentation Authority
For current operating state, use:
1. current executable behaviour and tests at the exact commit being assessed;
2. latest accepted Git/CI evidence tied to an exact SHA;
3. `README.md`;
4. `PROJECT_STATUS.md`;
5. `VERSION_MANIFEST.md`;
6. current architecture, governance and test-evidence documents.

Historical recovery, release and planning records remain evidence of prior stages and must not override later accepted state.

## Next Controlled Action
Complete manual hosted acceptance of the post-MRO-0 deployed app when practical. If it passes, record the result through a bounded evidence/documentation update if warranted and retain the stabilization freeze.

No MRO-1 or other feature expansion is pre-authorized.
