# ADR-008 — Trace Metadata Does Not Execute Calculations

## Status

Accepted for current portfolio architecture, subject to governed change control.

## Context

The application exposes formula metadata, calculation traces, explanations and planned evidence-presenter features such as SourceMate and calculation explorers. These layers improve explainability but can become a second calculation authority if they reproduce formulas independently.

## Decision

Formula and trace metadata explain authoritative calculations; they do not execute substitute calculations.

Trace identity, inputs, assumptions, versions and outputs must reconcile with the authoritative engine result. SourceMate, calculation-explorer and narrative layers remain read-only evidence presenters. Explanatory narrative cannot override executable results, change supplier status, alter ranking or create allocation.

## Decision Drivers

- Preserve one calculation authority.
- Improve explainability without introducing drift.
- Support audit and interview demonstration.
- Keep narrative generation separate from procurement decisions.
- Allow deterministic trace reconciliation.

## Considered Alternatives

- **Recalculate values from metadata in the presenter:** rejected due to duplicate logic and rounding drift.
- **Allow AI narrative to correct engine output:** rejected because narrative is not executable evidence.
- **Store only prose explanations:** rejected because structured trace identity and reconciliation are required.

## Consequences

Presenters consume immutable or governed trace evidence. Formula metadata may identify expressions, assumptions and source references, but engine code remains responsible for results. Mismatched trace and output must be treated as a defect or blocked state, not resolved through narrative.

## Risks and Controls

- **Risk:** trace presenter embeds copied formulas. **Control:** review rejects substitute calculations.
- **Risk:** AI explanation conflicts with engine output. **Control:** executable result prevails and conflict is disclosed.
- **Risk:** stale metadata describes an old engine version. **Control:** version linkage and reverification triggers.

## Scope

Formula traceability, calculation evidence, SourceMate, calculation explorers, explanations, audit views and exports containing trace metadata.

## Non-Scope

The formulas themselves, detailed business-rule definitions or implementation of SourceMate and calculation-explorer features.

## Evidence

- `FORMULA_TRACEABILITY_REGISTER.md`
- `PROJECT_ARCHITECTURE.md`
- `BUSINESS_RULES.md`
- `PROJECT_CONTROL.md`
- Relevant trace, formula-registry and reconciliation tests
- `modules/allocation_contract.py`
- `modules/multi_supplier_allocation.py`
- `modules/multi_supplier_allocation_adapter.py`
- Merged PRs #45, #46 and #47

## Reverification Triggers

Changes to formula metadata, trace schema, engine versions, explanation generation, SourceMate, calculation-explorer behaviour, reconciliation tests, exports or any presenter that derives business values.