# ADR-006 — Shared Deterministic Exactly-K Allocation Engine

## Status

Accepted for current portfolio architecture, subject to governed change control.

## Context

The programme requires one cross-category recommendation authority for allocating demand across exactly `K` suppliers while respecting eligibility, capacity and governed constraints. Legacy or UI-side allocation logic could create competing visible answers.

## Decision

`AIPC-MULTI-ALLOC-ENGINE-1.0` remains the shared deterministic exactly-K allocation recommendation authority.

The Gate 3A adapter prepares and validates governed inputs but does not execute allocation. Legacy allocation logic must not become a parallel visible authority. Deterministic supplier ordering, tie-breaking, capacity treatment, constraint validation and explicit failure statuses remain mandatory. Outputs are recommendations requiring human procurement approval.

## Decision Drivers

- Produce one reconciled allocation result across categories.
- Avoid parallel allocation authorities.
- Preserve deterministic review and testing.
- Keep contract construction separate from engine execution.
- Support auditable failure and feasibility states.

## Considered Alternatives

- **Retain multiple visible allocation engines:** rejected due to contradictory recommendations.
- **Execute allocation in the UI:** rejected because presentation would become authoritative.
- **Let the adapter perform allocation:** rejected because validation and optimization responsibilities should remain separate.

## Consequences

Gate 3B must route eligible governed inputs to the shared engine rather than recreate allocation logic. Compatibility with legacy logic must be explicit and non-authoritative. Allocation results must retain version, status, constraint evidence and human-review requirements.

## Risks and Controls

- **Risk:** legacy output appears beside the accepted result. **Control:** one visible authoritative allocation and controlled compatibility boundaries.
- **Risk:** nondeterministic tie outcomes. **Control:** stable ordering and deterministic tie-breaking tests.
- **Risk:** infeasible inputs produce misleading allocations. **Control:** explicit feasibility and failure statuses.

## Scope

Cross-category multi-supplier allocation recommendation, route integration, visible allocation output and downstream consumers.

## Non-Scope

Autonomous award, ERP execution, production optimization infrastructure or category-specific eligibility logic.

## Evidence

- `modules/allocation_contract.py`
- `modules/multi_supplier_allocation.py`
- `modules/multi_supplier_allocation_adapter.py`
- Relevant allocation and determinism tests
- `PROJECT_CONTROL.md`
- Merged PRs #45, #46 and #47

## Reverification Triggers

Changes to engine version, exactly-K semantics, constraint handling, tie-breaking, capacity rules, adapter execution responsibility, legacy allocation visibility or human-approval status.