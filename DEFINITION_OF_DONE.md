# Definition of Done

## Purpose

This policy defines the minimum evidence required before work may be described as complete. Completion is gate-specific. A passing test suite alone does not prove scope control, business correctness, merge completion or release readiness.

## Universal Requirements

Every governed change must have:

- explicit authorization and excluded scope;
- exact repository, branch, base SHA and head SHA;
- verified changed-file boundary;
- stated acceptance criteria;
- no unresolved blocking defect, review or evidence discrepancy;
- rollback or Git-revert path;
- exact CI or validation evidence appropriate to the change;
- human approval where procurement decisions or release promotion are involved;
- post-merge verification before the resulting `main` state is treated as accepted;
- current-state update in `PROJECT_CONTROL.md` when the operational state changes.

## Code Gate Done

A code gate is done only when:

1. Authorized behaviour and non-scope are explicit.
2. The branch was created from the required base SHA.
3. Only authorized files changed.
4. Focused tests cover the changed logic and material business risks.
5. Full `python -m pytest` passes.
6. Python compilation passes.
7. Streamlit smoke passes when the application or imports may be affected.
8. Calculations, eligibility, scoring, allocation, trace and exports reconcile where relevant.
9. Determinism, provenance and human-review boundaries remain intact.
10. CI evidence records workflow, run ID, job ID, runtime, test count and warnings.
11. Governed review accepts the implementation.
12. Merge uses the authorized method and expected-head protection where available.
13. Resulting `main` SHA and exact merge boundary are verified.

## Documentation-Only Gate Done

A documentation-only gate is done only when:

1. The changed-file list contains only authorized documentation paths.
2. No application, test, workflow, schema, dependency or deployment file changed.
3. Required headings, identifiers, references and staleness controls are present.
4. Documentation does not duplicate executable formulas or create a second source of truth.
5. Repository Quality Checks pass through the draft PR.
6. Full regression, compilation and smoke remain green when the existing workflow runs them.
7. No new warning is introduced.
8. Governed review confirms that statements are supported by repository evidence.
9. Post-merge verification records the resulting `main` SHA.

Documentation-only work does not require invented focused code tests when no executable behaviour changed. It still requires the repository's existing CI to remain green.

## Architecture Gate Done

An architecture gate is done only when:

- the material decision, alternatives, trade-offs and consequences are recorded;
- authoritative modules and boundaries are identified;
- business-rule ownership is unambiguous;
- migration and compatibility treatment are defined;
- rollback is possible;
- the decision does not create parallel authorities;
- relevant ADRs and `PROJECT_CONTROL.md` references are updated;
- implementation is not implied complete unless executable evidence exists.

## Programme Closure Done

A programme may close only when:

- every authorized gate is accepted or explicitly deferred;
- final contract versions and resulting `main` SHA are recorded;
- all accepted CI and manual evidence is identified;
- open limitations and residual risks are preserved;
- unsupported claims are removed;
- historical branches and recovery evidence are retained as authorized;
- next work is either explicitly authorized, deferred or out of scope;
- no active PR is falsely represented as merged or complete.

## Merge Done

A merge is done only when:

- the accepted head and base still match immediately before merge;
- no unresolved blocker or review-requested change exists;
- accepted CI remains applicable;
- the authorized merge method is used;
- expected-head protection is used where supported;
- the PR is confirmed closed and merged;
- the merge commit and resulting `main` SHA are captured;
- the exact files introduced by the merge are verified;
- post-merge CI is reported, or the absence of dispatch is explicitly recorded.

## Release Done

A release is done only when:

- the release is separately authorized;
- the exact approved `main` SHA is known;
- required CI, deployment and manual validation evidence applies to that SHA;
- version, tag and release notes agree;
- limitations and production classification remain accurate;
- no unsupported security, scale, verification or realized-savings claim is made;
- rollback and recovery instructions are available;
- the release tag points to the verified commit.

## Business-Risk Validation

Test volume is not the decision criterion. Evidence must address the material failure modes introduced or affected by the change, including as applicable:

- eligibility and evidence gating;
- currency and unit normalization;
- annualized cost and scenario propagation;
- capacity and exactly-K allocation constraints;
- assumption precedence and trace identity;
- UI, intelligence and export reconciliation;
- deterministic output and strict serialization;
- human procurement approval and prohibited automation.

Existing tests must not be removed solely to reduce run time or improve reported counts. Removal requires evidence of duplication, obsolescence or replacement by stronger coverage.

## Completion Language

Use precise states:

- implemented;
- CI-validated;
- governed-review accepted;
- merged;
- post-merge verified;
- released;
- deferred;
- not performed.

Do not use "complete" when a required later state remains outstanding.
