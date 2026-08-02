# ADR-001 — Authoritative Engines and Presentation Boundary

## Status

Accepted for current portfolio architecture, subject to governed change control.

## Context

The application contains category authorities, shared allocation contracts, deterministic engines, adapters, UI views, intelligence summaries and exports. Without an explicit authority boundary, presentation code could duplicate calculations and create conflicting outputs.

## Decision

Business and category engines remain authoritative for eligibility, cost, scoring, ranking and allocation. Presentation, sidebar, intelligence and export layers consume authoritative outputs and must not independently recalculate them.

Adapters may validate, normalize and construct governed contracts. They must not replace category authorities or introduce a second business-rule implementation. One accepted authoritative result must drive UI, intelligence and exports.

## Decision Drivers

- Prevent contradictory supplier recommendations.
- Preserve formula and business-rule traceability.
- Keep testing focused on one calculation authority.
- Support deterministic reconciliation across consumers.
- Minimize integration complexity before Gate 3B.

## Considered Alternatives

- **Duplicate calculations in each consumer:** rejected due to drift and reconciliation risk.
- **Make the UI the orchestration and calculation authority:** rejected because presentation changes would alter business outcomes.
- **Use adapters as replacement category engines:** rejected because category-specific authority and evidence would be lost.

## Consequences

Consumers must accept authoritative contracts and statuses. UI flexibility is limited to presentation and user-controlled inputs that are passed to governed engines. Integration work may require removal or isolation of legacy parallel calculations.

## Risks and Controls

- **Risk:** legacy logic remains visible beside the accepted result. **Control:** one visible authoritative output and explicit compatibility boundaries.
- **Risk:** presenters derive new business values. **Control:** tests and review reject presentation-layer calculations.
- **Risk:** adapters accumulate category rules. **Control:** category authorities remain responsible for category-specific decisions.

## Scope

Application routes, sidebar controls, intelligence summaries, dashboards and exports that consume procurement calculations.

## Non-Scope

Visual formatting, explanatory copy, layout and non-authoritative display transformations.

## Evidence

- `PROJECT_CONTROL.md`
- `PROJECT_ARCHITECTURE.md`
- `BUSINESS_RULES.md`
- `FORMULA_TRACEABILITY_REGISTER.md`
- `modules/allocation_contract.py`
- `modules/multi_supplier_allocation.py`
- `modules/multi_supplier_allocation_adapter.py`
- Relevant tests
- Merged PRs #45, #46, #47, #48 and #49

## Reverification Triggers

Changes to engine ownership, adapter responsibilities, UI calculation logic, export generation, route contracts, category authorities or authoritative result selection.