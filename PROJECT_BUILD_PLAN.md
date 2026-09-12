# Project Build Plan

## Product Objective
Maintain an auditable, human-controlled procurement decision-support portfolio application that improves supplier comparison, should-cost, TCO, risk, scenario, negotiation and executive decision quality without representing automated recommendations as supplier-award approval.

## Current Operating Position
The project is in **stabilization freeze / portfolio-interview mode**. The earlier recovery/v1.0.1 closure plan is historical and no longer the active build objective.

Current control anchors:
- stable branch: `main`;
- current `main` HEAD at Codex-governance bootstrap: `e75d930d06403bbefe919bace4d134d118e987df`;
- public portfolio baseline documented by the application: `dc05fcb86e5be53212443834b3d6c46cc5aeca5c`;
- latest accepted exact-head validation source: `b895815fe1c0511b7f025c53773ca2e5ba60dbdc`;
- frozen v1.2 historical baseline: `4803b1d72fa8a6509d9d7faf0e9decc677c447be`;
- frozen v1.1 historical baseline: `b85cd37aaae709058eb15350d680b18c03da46ba`.

## Current Build Policy
Routine feature expansion and cosmetic churn are closed. A new build is permitted only when explicitly authorized and justified as one of the following:
1. verified defect correction;
2. security or privacy hardening;
3. documentation/status reconciliation;
4. test/evidence/governance improvement;
5. material interview/launch-readiness correction;
6. separately approved future capability after a new business and architecture gate.

No item in this document constitutes blanket authorization to implement future features.

## Codex Bootstrap — Current Controlled Build
### Objective
Prepare the repository for governed Codex-assisted development without changing runtime behaviour or procurement business rules.

### Scope
- add root `AGENTS.md`;
- reconcile active status/version/recovery/build-control documents;
- preserve historical release evidence;
- establish least-privilege, branch-based, exact-head development rules;
- prohibit silent changes to formulas, schemas, thresholds, rankings, recommendation eligibility, approval controls and system boundaries.

### Branch / PR
- Branch: `codex/governance-bootstrap`
- Draft PR: #108

### Acceptance Criteria
- Diff contains only approved governance/documentation changes.
- No application runtime code, tests, dependency files or deployment configuration change unless separately authorized.
- Active control documents are internally consistent with the current stabilized portfolio state.
- Historical release and validation evidence remains preserved and clearly classified as historical exact-head evidence.
- PR exact head is captured before merge.
- Required repository checks, if triggered, complete successfully or are explicitly reviewed.
- Owner approves the exact verified head before merge.

## Future Controlled Build Sequence
For every later authorized task:
1. validate that the task is worth doing and consistent with stabilization policy;
2. define acceptance criteria and risk level;
3. start from current `main` on a focused branch;
4. read `AGENTS.md` and current control documents;
5. inspect affected architecture/business rules before editing;
6. make the smallest coherent change;
7. add/update targeted tests where behaviour changes;
8. run risk-appropriate checks, including regression/smoke checks when warranted;
9. review the complete diff for unrelated changes, secrets and governance drift;
10. update only the documentation required by the change;
11. open/update the PR with evidence, assumptions, risks and rollback;
12. verify the exact PR head before merge;
13. merge only after owner approval and required checks.

## Test Gates
Select gates according to change risk; do not claim a gate passed unless executed on the relevant head.

Potential gates include:
- Python import/compile checks;
- focused unit/regression tests;
- complete `python -m pytest` regression;
- Ruff governed checks;
- targeted mypy checks;
- dependency audit when dependencies change or release evidence requires it;
- Streamlit startup smoke;
- functional checks for affected procurement workflows;
- browser/mobile acceptance when visible behaviour materially changes;
- direct export/evidence inspection when outputs change.

## Approval Gates
Explicit approval is required before:
- expanding product scope;
- changing procurement formulas, schemas, scoring, thresholds, rankings or eligibility logic;
- introducing external AI/model/provider dependencies;
- enabling new outbound data transmission;
- changing authentication, secrets, deployment or production integration behaviour;
- creating/moving release tags or GitHub releases;
- deploying a governed change when deployment is not already an explicitly approved part of that task;
- merging a PR whose verified head has changed after approval.

## Persistent Excluded Scope
Unless a future architecture/governance decision explicitly changes the boundary:
- autonomous supplier award or approval;
- autonomous supplier qualification;
- production ERP write-back;
- production allocation execution;
- hidden or unverifiable recalculation;
- fabricated evidence or unsupported trace coverage;
- use of confidential supplier, contract, personal, credential or commercially sensitive data in the public demo;
- uncontrolled external AI-provider dependence.

## Historical Roadmap Integrity
Earlier v1.0.0, v1.0.1, v1.1 and v1.2 roadmap/build records remain historical evidence. Do not reinterpret their old pending actions as current work instructions merely because those documents remain in Git history.

## Next Controlled Action
Verify the final head and complete diff of PR #108. Merge only after the documentation/governance boundary is confirmed. Then treat the repository as Codex-ready for the next separately authorized task.
