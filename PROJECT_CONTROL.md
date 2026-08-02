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

## Staleness Rule

Any change to the current `main` SHA, active branch, active PR, base SHA, head SHA, merge-test SHA, accepted CI run or current gate invalidates the affected current-state fields until they are independently reverified. Estimates are not machine-verifiable facts.

## Identity and Classification

- Repository: `pratikoperations/AI-Procurement-Copilot`
- Project purpose: governed, explainable procurement decision support for sourcing analysis, supplier comparison, category calculations, risk, scenarios, allocation, traceability and business-readable outputs.
- Engineering classification: modular deterministic decision-support application with governed AI-assisted development.
- Portfolio classification: governed interview showcase / portfolio decision-support prototype.
- Production classification: not a production system and not currently a production candidate.
- Default branch: `main`
- Human procurement approval: mandatory.

## Current Verified Git State

- Current verified `main` SHA: `2896b1e36e66a65638f73e3f40dbfac96cd9f5b8`
- Current active programme: Shared Cross-Category Multi-Supplier Award and Allocation.
- Completed programme gate: Gate 3A — Common Route Adapter and Contract Construction.
- Current active implementation gate: none; Gate 3B is not authorized.
- Active implementation branch: none; stable operational ref is `main`.
- Active allocation-programme PR: none.
- Latest merged allocation PR: `#47`.
- Required implementation base SHA: not applicable until a new gate is authorized.
- Current implementation head SHA: not applicable.
- Current implementation merge-test SHA: not applicable.
- Governance working branch: `governance/project-control-foundation`.
- Governance gate: Gate 0B — Minimum Governance Foundation.
- Latest verified timestamp: `2026-08-02T11:35:00+05:30`.

## Accepted Contract Versions

- Gate 1 allocation contract: `AIPC-MULTI-ALLOC-1.0`
- Gate 2 allocation engine: `AIPC-MULTI-ALLOC-ENGINE-1.0`
- Gate 3A route adapter: `AIPC-MULTI-ALLOC-ADAPTER-1.0`

## Accepted Assurance Evidence

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
- Post-merge CI: no pull-request-triggered workflow dispatch was observed for merge commit `2896b1e36e66a65638f73e3f40dbfac96cd9f5b8`.
- Manual browser/mobile validation: not performed for Gate 3A; automated tests and smoke do not constitute device certification.

## Completed Scope

- Gate 1 shared immutable allocation request, supplier-input and feasibility foundation.
- Gate 2 isolated deterministic exactly-K allocation recommendation engine.
- Gate 3A isolated governed route adapter with explicit eligibility, capacity, TCO, score and evidence-origin controls.
- Strict deterministic JSON, source/provenance controls, unsupported-evidence failure and mandatory human review.

## Currently Authorized Scope

Gate 0B only:

- create `PROJECT_CONTROL.md`;
- create `DEFINITION_OF_DONE.md`;
- create `SIMPLICITY_GATE.md`;
- create `VERIFICATION_POLICY.md`;
- preserve a documentation-only four-file boundary.

## Deferred Scope

- Gate 3B sidebar controls and application-route integration.
- Gate 3C Procurement Intelligence and risk unification.
- Gate 3D export and executive-output unification.
- Gate 3E Steel and mandatory category adapters.
- Gate 3F full regression and physical browser/mobile validation.
- ADR foundation, test-risk register, component explainers and historical-document reconciliation.
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
- `PROJECT_ARCHITECTURE.md`
- `BUSINESS_RULES.md`
- `FORMULA_TRACEABILITY_REGISTER.md`
- `DATA_DICTIONARY.md`
- `docs/07_GOVERNANCE_AND_LIMITATIONS.md`
- `docs/EAS_BIV_FINAL_CLOSURE.md`

## Current Risks

- Repository historical status documents contain older baselines and must not be used as the current operational state without re-verification.
- Future Gate 3B must not mix Gate 2 visible allocation with legacy intelligence allocation.
- Partial adapter evidence must be clearly labelled before UI display.
- `evidence_origin` may need promotion to a first-class route/result field during Gate 3B design.
- Export and Power BI work remain blocked until one authoritative allocation result drives every consumer.

## Next Authorized Action

Complete Gate 0B through a draft documentation-only PR and governed review. Do not begin Gate 3B until Gate 0B is accepted and merged or separately reprioritized by explicit authorization.

## Planning Estimates

- Estimated Gate 0B effort: `4–7 engineering-equivalent hours`.
- Estimated remaining multi-supplier integration effort: `18–30 engineering-equivalent hours`.
- Gate 0B completion at document creation: implementation in progress; not accepted or merged.
- Multi-supplier programme completion estimate: approximately `78–81%`.
- Overall project completion estimate: approximately `80%` of the current governed portfolio roadmap.
- Last verification date: `2026-08-02`.
