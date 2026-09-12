# AGENTS.md — AI Procurement Copilot

## Purpose
These instructions govern all AI-assisted changes in this repository. They apply to Codex and any other coding agent operating on this project.

## Project Position
- This repository is a public portfolio / interview demonstrator, not production enterprise software.
- The current product is under stabilization freeze. Do not expand scope unless the task explicitly authorizes a new governed capability.
- Human procurement approval remains mandatory. The application must not execute sourcing awards, supplier approvals, production allocations, purchase orders, ERP write-back, or other autonomous procurement actions.
- SourceMate remains read-only and evidence-bounded. Do not silently add external LLM, RAG, browsing, hidden recalculation, autonomous recommendation, or transactional authority.
- Use synthetic or sanitized data for public-demo workflows. Never commit confidential supplier quotations, contracts, personal data, credentials, secrets, or commercially sensitive information.

## Source of Truth and Recovery Order
Before material work, inspect the current branch, latest commit, relevant code, tests, and current documentation.

When documentation conflicts:
1. Do not silently choose one document and proceed.
2. Prefer current executable behaviour and the latest accepted Git / CI evidence over clearly stale narrative status text.
3. Treat `README.md` as the current public-position summary unless a newer committed governance record explicitly supersedes it.
4. Report contradictions and request or record a reconciliation decision before changing business behaviour.

Relevant documents include:
- `README.md`
- `ARCHITECTURE.md` and `docs/04_ARCHITECTURE.md`
- `BUSINESS_RULES.md`
- `DATA_DICTIONARY.md`
- `CONTRIBUTING.md`
- `DECISION_LOG.md`
- `CHANGELOG.md`
- `BUILD_HISTORY.md`
- `PROJECT_STATUS.md`
- `AI_HANDOFF_GUIDE.md`
- `SETUP_GUIDE.md`
- `PROJECT_ARCHITECTURE.md`
- applicable evidence / closure documents under `docs/`

## Mandatory Pre-Change Procedure
For every material change:
1. Confirm the requested objective and acceptance criteria.
2. Inspect all files and tests relevant to the requested change.
3. State the intended implementation scope and likely files to change.
4. Identify business-rule, data-schema, governance, security, privacy, deployment, and backward-compatibility impacts.
5. Stop and report if the request conflicts with a frozen contract, existing governance boundary, or accepted evidence baseline.

Do not modify files outside the approved task scope.

## Procurement and Calculation Controls
- Existing business services and governed calculation logic are authoritative.
- Never invent or silently alter formulas, FX rates, units, defaults, thresholds, scoring weights, qualification rules, capacities, risk values, category assumptions, or recommendation logic.
- Formula metadata is documentation unless the existing architecture explicitly executes it.
- Preserve original and normalized quotation data semantics.
- Preserve evidence provenance, validation gates, trace identities, reconciliation semantics, and explicit unsupported/deferred states.
- Unknown, missing, unsupported, or unverified evidence must remain explicit; do not fabricate completion or certainty.
- Any change to calculations, scoring, eligibility, TCO, allocation, recommendation language, or evidence contracts requires targeted regression tests and explicit impact reporting.

## Architecture Controls
- Preserve existing module and service boundaries unless an architecture change is explicitly approved.
- Prefer the smallest coherent change that satisfies the task.
- Avoid unrelated refactors, formatting churn, dependency changes, or broad rewrites.
- Do not introduce new frameworks, persistence layers, external services, agents, databases, APIs, or infrastructure without explicit approval and a documented rationale.
- Keep demo / portfolio claims separate from production-readiness claims.

## Security, Privacy, and Network
- Never commit secrets, tokens, keys, passwords, private certificates, or real confidential procurement data.
- Do not weaken upload warnings, validation, privacy messaging, or data-handling boundaries.
- Network access is exceptional. Use it only when required by the approved task and report what external resource is needed and why.
- Do not add telemetry, analytics, tracking, external model calls, or third-party data transmission without explicit approval.
- Dependency additions or upgrades require justification, compatibility review, and security / vulnerability checks where tooling exists.

## Testing and Verification
For material code changes, run the relevant subset first, then the governed full checks when appropriate.

Baseline commands include:
```bash
python -m pytest
```

Also run applicable project checks already defined in CI, including compilation, Ruff, targeted type checks, dependency audit, Streamlit smoke, and browser/mobile acceptance when the changed area requires them.

Rules:
- Never claim a test or check passed unless it was actually executed and the result is available.
- Report exact commands, pass/fail counts, warnings, skipped checks, and blockers.
- Add targeted regression tests for corrected defects and changed business logic.
- Visible UI or export changes should include appropriate screenshots / artifacts or equivalent acceptance evidence when the project workflow requires them.
- A passing targeted test suite does not replace required full-regression or acceptance gates.

## Git and Change Control
- `main` is protected by process even where repository settings do not technically enforce every control.
- Never push implementation directly to `main`.
- Work on a focused branch using the repository naming conventions where practical: `fix/`, `feature/`, `test/`, `docs/`, or a specifically approved governance branch.
- Keep commits scoped and reviewable.
- Do not force-push, rewrite shared history, delete branches, or alter tags/releases unless explicitly instructed.
- Do not merge a pull request automatically unless explicitly authorized for that exact PR after verification.
- Before recommending merge, verify the PR head SHA has not changed from the validated head (exact-head control).
- If the head changes after validation, required checks must be re-evaluated against the new head.

## Pull Request Requirements
A material PR should state:
- problem / objective;
- approved scope and acceptance criteria;
- files / workflows affected;
- architecture, business-rule, schema, security, privacy, and deployment impact;
- tests and checks executed with results;
- assumptions and unresolved risks;
- rollback method;
- exact validated head SHA when recommending merge.

## Documentation Discipline
Update documentation only when the implementation or governed project state materially changes.

Where applicable update:
- `README.md` for public-facing current position;
- `CHANGELOG.md` for meaningful delivered changes;
- `BUILD_HISTORY.md` for governed build history;
- `DECISION_LOG.md` for material decisions;
- relevant architecture, business-rule, data, test-evidence, closure, or release records.

Do not overwrite frozen historical release evidence to make later work appear part of an earlier release.

## Deployment and Hosted App
- Do not deploy, change Streamlit secrets, alter production/hosted configuration, create releases/tags, or change externally visible hosting state unless explicitly authorized.
- A local or CI pass does not by itself prove hosted acceptance.
- When a hosted defect or launch-readiness task requires it, keep hosted manual acceptance as a separate evidence gate.

## Agent Behaviour
- Inspect before editing.
- Prefer evidence over assumption.
- Ask or stop when a material ambiguity could change business behaviour, architecture, governance, security, privacy, or public claims.
- Do not broaden an approved task because another improvement appears convenient.
- Do not conceal uncertainty, skipped checks, warnings, test failures, or scope deviations.
- Finish each task with a concise change summary, verification evidence, residual risks, and recommended next action.
