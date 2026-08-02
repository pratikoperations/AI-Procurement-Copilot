# Project Control

## Purpose

This document is the current operational index for `pratikoperations/AI-Procurement-Copilot`. It summarizes verified state and points to higher-authority Git, CI, executable and governance evidence. It does not replace Git history, CI evidence, code, tests, architecture documentation, business rules, formula traceability, programme closure records or human approval.

## Source-of-Truth Hierarchy

1. Immutable Git objects and current refs.
2. Executed CI and validation evidence tied to exact SHAs.
3. Executable contracts, code and tests.
4. `PROJECT_CONTROL.md`.
5. ADRs, architecture, business rules and recovery documents.
6. PR descriptions and closure records.
7. Conversation history.

When sources conflict, the higher source prevails. A narrative statement cannot override an exact ref, executable behaviour or CI result.

### Temporary `AI_HANDOFF_GUIDE.md` Transition Rule

Until `AI_HANDOFF_GUIDE.md` is reconciled in Gate 0F:

- Git objects, exact CI evidence, executable contracts and this `PROJECT_CONTROL.md` hierarchy govern current repository state.
- `AI_HANDOFF_GUIDE.md` remains applicable for protected areas, secrets, scope discipline and change protocol.
- Its historical baseline, frozen-v1.0.0 branch statements and mandatory current-document list must be independently reverified before use.
- Conflicts concerning current state are resolved using the hierarchy in this file.

## Staleness and Self-Reference Rule

Any change to the current `main` SHA, active branch, active PR, base SHA, head SHA, merge-test SHA, accepted CI run or current gate invalidates the affected current-state fields until they are independently reverified. Estimates are not machine-verifiable facts.

This closure document records the verified Gate 0B merge SHA. The closure branch head, closure PR merge-test SHA and any later resulting `main` SHA remain externally governed by Git and CI. This file must not attempt to embed the SHA of the commit currently modifying it. Merging a later closure PR triggers this staleness rule for affected moving identifiers.

## Identity and Classification

- Repository: `pratikoperations/AI-Procurement-Copilot`
- Project purpose: governed, explainable procurement decision support for sourcing analysis, supplier comparison, category calculations, risk, scenarios, allocation, traceability and business-readable outputs.
- Engineering classification: modular deterministic decision-support application with governed AI-assisted development.
- Portfolio classification: governed interview showcase / portfolio decision-support prototype.
- Production classification: not a production system and not currently a production candidate.
- Default branch: `main`.
- Human procurement approval: mandatory.

## Current Verified Repository State

- Current verified `main` SHA: `c5b420c0eb21c957593c6042ce30b1dc18da8f2a`.
- Gate 0B status: accepted, merged and post-merge verified.
- Merged governance PR: `#48`.
- Gate 0B merge commit: `c5b420c0eb21c957593c6042ce30b1dc18da8f2a`.
- Gate 0B merged at: `2026-08-02T06:27:47Z`.
- Latest verified timestamp: `2026-08-02T12:03:00+05:30`.

## Stable Allocation-Programme State

- Current allocation programme: Shared Cross-Category Multi-Supplier Award and Allocation.
- Completed allocation gate: Gate 3A — Common Route Adapter and Contract Construction.
- Current allocation implementation gate: none.
- Gate 3B: not authorized.
- Active allocation implementation branch: none; stable operational ref is `main`.
- Active allocation-programme PR: none.
- Latest merged allocation PR: `#47`.
- Required allocation implementation base SHA: not applicable until a new gate is authorized.
- Current allocation implementation head SHA: not applicable.
- Current allocation implementation merge-test SHA: not applicable.

## Governance State After Gate 0B Merge

- Governance programme: Governed AI-Assisted Development Operating Method.
- Completed governance gate: Gate 0B — Minimum Governance Foundation.
- Active governance implementation gate: none.
- Active governance implementation branch: none.
- Active governance PR: none after PR `#48` merge.
- Latest merged governance PR: `#48`.
- Retained governance branch: `governance/project-control-foundation`.
- Gate 0C: not authorized.
- Gate 0B closure branch: `governance/gate-0b-control-closure`; its current head and future PR merge-test remain external Git/CI evidence.

## Accepted Contract Versions

- Gate 1 allocation contract: `AIPC-MULTI-ALLOC-1.0`.
- Gate 2 allocation engine: `AIPC-MULTI-ALLOC-ENGINE-1.0`.
- Gate 3A route adapter: `AIPC-MULTI-ALLOC-ADAPTER-1.0`.

## Accepted Gate 3A Assurance Evidence

- Workflow: Quality Checks.
- Accepted run number: `845`.
- Run ID: `30734046622`.
- Job ID: `91459345517`.
- Accepted merge-test SHA: `f976fa6b866bce8941a6e663fee0099b4b067ed2`.
- Python: `3.11.15`.
- Test result: `1319 passed`, `0 failures`, `0 errors`.
- Python compilation: passed.
- Streamlit smoke: passed.
- Warning boundary: one pre-existing pandas `FutureWarning`; no Gate 3A warning.
- Post-merge CI: no pull-request-triggered workflow dispatch was observed for Gate 3A merge commit `2896b1e36e66a65638f73e3f40dbfac96cd9f5b8`.
- Manual browser/mobile validation: not performed for Gate 3A; automated tests and smoke do not constitute device certification.

## Accepted Gate 0B Assurance Evidence

- Workflow: Quality Checks.
- Accepted run number: `848`.
- Run ID: `30735635178`.
- Job ID: `91463833522`.
- Accepted merge-test SHA: `1601b4296aaf7781a4b85b408e3c7f591331a7db`.
- Accepted head SHA: `f7bce982fc814d56b817b6dab24f96fe368607f9`.
- Python: `3.11.15`.
- Test result: `1319 passed`, `0 failures`, `0 errors`.
- Python compilation: passed.
- Streamlit smoke: passed.
- Warning boundary: one pre-existing pandas `FutureWarning`; no new Gate 0B warning.
- Post-merge CI: no pull-request-triggered workflow dispatch was observed for Gate 0B merge commit `c5b420c0eb21c957593c6042ce30b1dc18da8f2a`.

Historical Gate 0B run `847` remains pre-correction evidence only and is subordinate to accepted run `848`.

## Completed Scope

- Gate 1 shared immutable allocation request, supplier-input and feasibility foundation.
- Gate 2 isolated deterministic exactly-K allocation recommendation engine.
- Gate 3A isolated governed route adapter with explicit eligibility, capacity, TCO, score and evidence-origin controls.
- Strict deterministic JSON, source/provenance controls, unsupported-evidence failure and mandatory human review.
- Gate 0B governance foundation merged on `main`:
  - `PROJECT_CONTROL.md`;
  - `DEFINITION_OF_DONE.md`;
  - `SIMPLICITY_GATE.md`;
  - `VERIFICATION_POLICY.md`.
- Gate 0B introduced no executable, architecture, test, CI, dependency, deployment or hosted-behaviour change.

## Currently Authorized Scope

Gate 0B closure only:

- reconcile the merged Gate 0B state in `PROJECT_CONTROL.md`;
- preserve a one-file documentation-only boundary;
- run the existing Quality Checks through a draft PR;
- keep the closure PR draft and unmerged until governed review.

## Deferred Scope

- Gate 0C critical ADR foundation.
- Gate 3B sidebar controls and application-route integration.
- Gate 3C Procurement Intelligence and risk unification.
- Gate 3D export and executive-output unification.
- Gate 3E Steel and mandatory category adapters.
- Gate 3F full regression and physical browser/mobile validation.
- Test-risk register, component explainers and historical-document reconciliation.
- Power BI until authoritative export unification is accepted.
- Production authentication, database, ERP integration, persistence, observability, high availability and disaster-recovery infrastructure.

## Prohibited Scope

- Autonomous supplier award or production allocation.
- ERP write-back or approval persistence.
- Realized-savings claims without organizational evidence.
- Unverified supplier-capacity claims.
- Silent eligibility, capacity, TCO or score inference.
- A second scoring, allocation or business-rule authority.
- Presentation-layer reimplementation of authoritative calculations.
- Production infrastructure added only for portfolio appearance.

## Known Limitations

- The application is a governed portfolio showcase, not an enterprise production system.
- Supplier, capacity, ESG, performance and risk evidence may be synthetic, supplied or incomplete unless independently verified.
- No enterprise identity, authorization, production database, multi-user concurrency, persistent approval workflow, live ERP write-back, production observability, HA or DR is claimed.
- Physical Android, browser and accessibility certification is not implied by automated tests.
- Gate 3A remains isolated from application routes.

## Architecture Constraints

- Existing business engines remain authoritative and separate from presentation.
- Eligibility remains distinct from scoring and ranking.
- Comparison calculations use a governed normalized currency basis.
- Formula metadata and explanation layers do not execute substitute calculations.
- Category-specific rules remain in category authorities; shared adapters do not silently reimplement them.
- Outputs remain recommendations requiring human procurement approval.

## Relevant Evidence and Records

- PR `#45`: Gate 1 contract and feasibility.
- PR `#46`: Gate 2 deterministic exactly-K engine.
- PR `#47`: Gate 3A governed route adapter.
- PR `#48`: Gate 0B minimum governance foundation, closed and merged.
- `PROJECT_ARCHITECTURE.md`.
- `BUSINESS_RULES.md`.
- `FORMULA_TRACEABILITY_REGISTER.md`.
- `DATA_DICTIONARY.md`.
- `docs/07_GOVERNANCE_AND_LIMITATIONS.md`.
- `docs/EAS_BIV_FINAL_CLOSURE.md`.

## Current Risks

- Repository historical status documents contain older baselines and must not be used as the current operational state without re-verification.
- `AI_HANDOFF_GUIDE.md` contains historical current-state and branch statements pending Gate 0F reconciliation.
- Future Gate 3B must not mix Gate 2 visible allocation with legacy intelligence allocation.
- Partial adapter evidence must be clearly labelled before UI display.
- `evidence_origin` may need promotion to a first-class route/result field during Gate 3B design.
- Export and Power BI work remain blocked until one authoritative allocation result drives every consumer.

## Next Recommended Decision

After this closure update is accepted and merged, explicitly prioritize one of:

1. Gate 0C — critical ADR foundation; or
2. Gate 3B — governed application-route and sidebar planning.

Neither gate is currently authorized. Power BI remains blocked until authoritative export unification.

## Planning and Effort Evidence

- Gate 0B completion estimate: `100%`.
- Governance-integration completion estimate: approximately `70%`.
- Multi-supplier programme completion estimate: approximately `78–81%`.
- Overall project completion estimate: approximately `83–85%` of the current governed portfolio roadmap.
- Gate 0B cumulative engineering-equivalent effort estimate: approximately `13.65–23.6 hours`.
- Estimated remaining multi-supplier integration effort: `18–30 engineering-equivalent hours`.
- Last verification date: `2026-08-02`.
