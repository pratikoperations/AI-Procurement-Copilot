# Verification Policy

## Purpose

Verification is tied to exact repository state. Evidence is reusable only while the relevant Git objects, executable contracts, environment and claimed behaviour remain unchanged and no discovered defect invalidates it.

## Authority

Git and executed CI remain higher authority than documentation. `PROJECT_CONTROL.md` is a current index, not executable evidence. Historical records are retained and must not be rewritten as current facts without re-verification. Conversation history is not authoritative.

## Mandatory Verification Triggers

| Trigger | Required action |
|---|---|
| `main` SHA changes | Re-fetch `main`, identify the merged change, verify exact file boundary and capture applicable post-merge CI. |
| Active branch changes | Re-establish branch purpose, starting SHA, authorized scope and exclusions. |
| Base SHA changes | Reassess compatibility, recompute or re-fetch merge-test state and invalidate prior base-specific review. |
| PR state changes | Re-fetch open/draft/ready/closed/merged state and timestamps. |
| Head SHA changes | Treat prior head review and CI as non-current until the new head is verified. |
| Merge-test SHA changes | Verify CI against the new merge-test; do not reuse an earlier merge-test result. |
| Changed-file list changes | Re-audit scope boundary and affected architecture, tests, schemas and documentation. |
| Test files change | Reassess intended risk coverage and run focused plus full regression evidence as applicable. |
| CI workflow changes | Verify commands, triggers, runtime, permissions and the meaning of future green runs. |
| Dependency changes | Run full CI and assess compatibility, security and runtime effects. |
| Deployment changes | Perform fresh deployment smoke and required physical browser/device checks. |
| Runtime or environment changes | Re-run compilation, tests and smoke in the changed environment. |
| Architecture changes | Update or create the material ADR and verify authority boundaries and rollback. |
| Calculation or business-rule changes | Run focused business-risk tests, full CI and trace/output reconciliation. |
| Eligibility or scoring changes | Verify fail-closed eligibility, threshold, ranking and award-language controls. |
| Allocation changes | Verify feasibility, exactly-K, share, capacity, continuity, determinism and reconciliation. |
| Export-schema changes | Verify strict JSON/Excel structure, compatibility and equality with authoritative outputs. |
| Defect discovery | Classify impact and invalidate all evidence that relied on the defective behaviour. |
| Governance requirement changes | Update affected policies and re-review active work against the new requirement. |
| Merge authorization | Re-fetch PR, head, base, merge-test, changed files, reviews, threads and CI immediately before mutation. |
| Release authorization | Verify exact resulting `main` SHA, version, tag target, CI, deployment and manual acceptance evidence. |

## Evidence Reuse Conditions

Prior evidence may be reused only when all conditions hold:

1. The exact relevant commit or merge-test SHA is unchanged.
2. The relevant dependencies, runtime and workflow meaning are unchanged.
3. No authoritative upstream contract used by the behaviour changed.
4. The evidence directly covers the claim being made.
5. No later defect or review finding invalidates it.
6. Manual evidence is reused only for the same hosted build, route, device and observable behaviour.

When any condition fails, mark the evidence as historical and perform fresh verification.

## Required Verification Record

Every governed review, merge or release record must capture as applicable:

- repository;
- branch;
- base SHA;
- head SHA;
- merge-test SHA;
- PR number and state;
- changed-file list;
- workflow name;
- run number and run ID;
- job ID;
- runtime version;
- test count and result;
- compilation result;
- smoke result;
- warnings;
- manual validation state;
- verification timestamp;
- reviewer or evidence owner;
- accepted limitations;
- next authorized action.

## Verification Depth by Change Type

### Documentation-only

- verify exact Markdown boundary and required content;
- confirm no executable, test, workflow, dependency, schema or deployment file changed;
- run the repository's existing CI through the PR;
- do not invent code tests for prose-only behaviour.

### Presentation-only

- verify no authoritative calculation changed;
- run full CI and direct UI checks;
- reconcile displayed values with authoritative outputs;
- perform narrow/mobile checks when layout is affected.

### Business logic

- focused unit and adversarial tests;
- full regression;
- compilation and smoke;
- business-risk evaluation;
- deterministic and provenance checks;
- UI/export reconciliation where consumed.

### Architecture or contract

- exact compatibility assessment;
- material ADR;
- version and serialization checks;
- consumer inventory;
- migration and rollback plan;
- full CI and governed review.

### Deployment or release

- exact artifact/commit identity;
- environment and secrets boundary;
- hosted smoke;
- required physical acceptance;
- rollback and recovery evidence;
- tag and release identity.

## Conflict Resolution

1. Current refs and immutable Git objects override document claims.
2. CI evidence applies only to the exact checked-out SHA.
3. Executable contracts, code and tests override narrative descriptions of implemented behaviour.
4. ADRs govern accepted intent but do not prove implementation.
5. PR descriptions define authorized scope but diffs and CI prove adherence.
6. `PROJECT_CONTROL.md` must be refreshed when its staleness rule is triggered.
7. Chat or memory cannot override repository evidence.

## Procurement Governance

Verification must preserve:

- human procurement review and approval;
- no autonomous award;
- no silent eligibility or capacity inference;
- source and assumption provenance;
- deterministic business rules;
- distinction between supplied, synthetic, derived and verified evidence;
- no realized-savings claim without organizational evidence;
- portfolio-versus-production limitations.

## Merge and Release Stop Conditions

Stop before merge or release when:

- head, base or merge-test moved;
- the file boundary expanded without authorization;
- CI is missing, failing or no longer applicable;
- a review requests changes or an unresolved blocker remains;
- current-control facts conflict with Git;
- rollback is unavailable;
- human approval is required but absent;
- production or verification claims exceed the available evidence.
