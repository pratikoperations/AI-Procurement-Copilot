# ADR-004 — Eligibility Distinct From Scoring and Ranking

## Status

Accepted for current portfolio architecture, subject to governed change control.

## Context

Procurement decisions require a clear separation between whether a supplier is technically and commercially eligible and how eligible suppliers are scored or ranked. Blending these stages can allow a high score to conceal a mandatory failure.

## Decision

Eligibility is a gating decision. Scoring and ranking apply only after governed eligibility treatment.

A supplier cannot become eligible because of a strong score, low price or favourable rank. Missing technical eligibility must not silently default to `true`. Missing supplier capacity must not be inferred from annual demand or annual volume. Any exclusion, failure or missing mandatory evidence must remain explicit in the result contract and presentation.

## Decision Drivers

- Protect mandatory technical and sourcing constraints.
- Prevent attractive commercial scores from overriding disqualifying evidence.
- Preserve explainability and auditability.
- Support deterministic allocation feasibility.
- Avoid unsafe defaults for incomplete evidence.

## Considered Alternatives

- **Blend eligibility into a weighted score:** rejected because hard constraints become negotiable.
- **Default missing eligibility to eligible:** rejected because absence of evidence is not approval.
- **Infer capacity from demand:** rejected because demand does not prove supplier capability.

## Consequences

Contracts, adapters, engines, UI and exports must retain separate eligibility, reason and capacity fields. Ranking views must not imply that excluded suppliers remain award candidates. Incomplete mandatory evidence may block readiness rather than produce a recommendation.

## Risks and Controls

- **Risk:** UI sorts all suppliers together and obscures exclusions. **Control:** explicit eligibility status and filtered ranking semantics.
- **Risk:** category routes provide inconsistent evidence. **Control:** governed adapter validation and contract-construction failure.
- **Risk:** new scoring logic reintroduces eligibility weights. **Control:** architecture and test review.

## Scope

Supplier qualification, technical eligibility, capacity evidence, scoring, ranking, allocation feasibility and their presentation.

## Non-Scope

Category-specific technical criteria or score-weight formulas, which remain in authoritative source documents and engines.

## Evidence

- `BUSINESS_RULES.md`
- `PROJECT_ARCHITECTURE.md`
- `modules/allocation_contract.py`
- `modules/multi_supplier_allocation.py`
- `modules/multi_supplier_allocation_adapter.py`
- Relevant eligibility, capacity and allocation tests
- Merged PRs #45, #46 and #47

## Reverification Triggers

Changes to eligibility fields, capacity treatment, scoring inputs, ranking logic, category qualification, missing-evidence handling, allocation feasibility or UI ranking semantics.